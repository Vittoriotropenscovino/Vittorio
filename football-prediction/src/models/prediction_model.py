"""Prediction model - Core prediction engine"""

import logging
import numpy as np
from scipy.stats import poisson
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class PredictionModel:
    """
    Hybrid prediction model combining multiple methods:
    - Weighted scoring system
    - Poisson distribution (goals-based)
    - ML model (if available)
    """

    def __init__(self, features: Dict, config: Dict):
        """
        Initialize prediction model

        Args:
            features: Processed features dict from DataProcessor
            config: Model configuration (weights, parameters)

        Raises:
            ValueError: If features is None or empty
        """
        if not features:
            raise ValueError("Features dictionary cannot be None or empty")

        self.features = features
        self.config = config
        self.weights = config.get('weights', self._default_weights())

    def _default_weights(self) -> Dict:
        """Default category weights"""
        return {
            'form': 0.25,
            'squad_quality': 0.20,
            'motivation': 0.15,
            'physical_condition': 0.15,
            'home_advantage': 0.10,
            'tactical': 0.10,
            'psychological': 0.05
        }

    def predict(self) -> Dict:
        """
        Generate complete prediction

        Returns:
            Dict with probabilities, expected goals, scores, confidence
        """
        logger.info("Generating prediction with ensemble methods...")

        # Method 1: Weighted scoring
        scoring_probs = self._scoring_method()

        # Method 2: Poisson distribution
        poisson_probs = self._poisson_method()

        # Method 3: ML model (if available)
        ml_probs = self._ml_method() if self.config.get('use_ml') else None

        # Ensemble combination
        final_probs = self._ensemble_predictions(
            scoring_probs,
            poisson_probs,
            ml_probs
        )

        # Calculate additional metrics (reuse poisson_probs to avoid recalculation)
        expected_goals = self._calculate_expected_goals(poisson_probs)
        most_likely_score = self._most_likely_scoreline(expected_goals)

        result = {
            "probabilities": final_probs,
            "expected_goals": expected_goals,
            "most_likely_score": most_likely_score,
            "confidence": self._calculate_confidence(final_probs, scoring_probs, poisson_probs),
            "method_breakdown": {
                "scoring": scoring_probs,
                "poisson": poisson_probs,
                "ml": ml_probs
            }
        }

        logger.info(f"Prediction complete: {final_probs}")
        return result

    def _scoring_method(self) -> Dict:
        """
        Weighted scoring method

        Combines multiple factors with configurable weights
        """
        scores = {'home': 0.0, 'away': 0.0}

        # 1. Form (25%)
        scores['home'] += self.features.get('home_form', 5.0) * self.weights['form']
        scores['away'] += self.features.get('away_form', 5.0) * self.weights['form']

        # 2. Squad Quality (20%)
        scores['home'] += self.features.get('home_squad_quality', 5.0) * self.weights['squad_quality']
        scores['away'] += self.features.get('away_squad_quality', 5.0) * self.weights['squad_quality']

        # 3. Motivation (15%)
        scores['home'] += self.features.get('home_motivation', 5.0) * self.weights['motivation']
        scores['away'] += self.features.get('away_motivation', 5.0) * self.weights['motivation']

        # 4. Physical Condition (15%)
        scores['home'] += self.features.get('home_physical_condition', 5.0) * self.weights['physical_condition']
        scores['away'] += self.features.get('away_physical_condition', 5.0) * self.weights['physical_condition']

        # 5. Home Advantage (10%) - only for home team
        scores['home'] += self.features.get('home_field_advantage', 5.0) * self.weights['home_advantage']

        # 6. Tactical Matchup (10%)
        tactical_score = self.features.get('tactical_matchup_score', 0)
        scores['home'] += max(tactical_score, 0) * 10 * self.weights['tactical']
        scores['away'] += max(-tactical_score, 0) * 10 * self.weights['tactical']

        # 7. Psychological (H2H) (5%)
        h2h_factor = self.features.get('h2h_home_advantage', 0)
        scores['home'] += max(h2h_factor, 0) * 10 * self.weights['psychological']
        scores['away'] += max(-h2h_factor, 0) * 10 * self.weights['psychological']

        # Convert scores to probabilities
        diff = scores['home'] - scores['away']

        # Logistic function for home/away win probabilities
        prob_home_raw = 1 / (1 + np.exp(-0.4 * diff))
        prob_away_raw = 1 - prob_home_raw

        # Draw probability (Gaussian on difference)
        prob_draw = 0.35 * np.exp(-0.8 * diff**2)

        # Normalize
        total = prob_home_raw + prob_away_raw + prob_draw

        return {
            '1': prob_home_raw / total,
            'X': prob_draw / total,
            '2': prob_away_raw / total
        }

    def _poisson_method(self) -> Dict:
        """
        Poisson distribution method based on expected goals

        Uses team attacking/defensive strength
        """
        # Get average goals
        home_attack = self.features.get('home_avg_goals', 1.5)
        away_defense = self.features.get('away_avg_conceded', 1.2)
        away_attack = self.features.get('away_avg_goals', 1.3)
        home_defense = self.features.get('home_avg_conceded', 1.2)

        # Home advantage multiplier
        home_advantage_multiplier = 1 + (self.features.get('home_field_advantage', 6.0) - 5.0) * 0.05

        # Expected goals (lambda for Poisson)
        lambda_home = ((home_attack + away_defense) / 2) * home_advantage_multiplier
        lambda_away = (away_attack + home_defense) / 2

        # Calculate probability matrix (0-0 to 5-5)
        prob_matrix = np.zeros((6, 6))

        for home_goals in range(6):
            for away_goals in range(6):
                prob_matrix[home_goals, away_goals] = (
                    poisson.pmf(home_goals, lambda_home) *
                    poisson.pmf(away_goals, lambda_away)
                )

        # Aggregate to 1X2
        prob_home = np.sum(np.tril(prob_matrix, -1))  # Home wins
        prob_draw = np.sum(np.diag(prob_matrix))      # Draws
        prob_away = np.sum(np.triu(prob_matrix, 1))   # Away wins

        return {
            '1': prob_home,
            'X': prob_draw,
            '2': prob_away,
            '_lambda_home': lambda_home,
            '_lambda_away': lambda_away,
            '_prob_matrix': prob_matrix
        }

    def _ml_method(self) -> Optional[Dict]:
        """
        Machine learning model prediction

        Loads pre-trained sklearn model if available
        """
        try:
            import joblib

            model_path = self.config.get('ml_model_path', 'models_ml/match_predictor_v1.pkl')
            model = joblib.load(model_path)

            # Prepare feature vector
            X = self._prepare_ml_features()

            # Predict probabilities
            probs = model.predict_proba(X)[0]

            logger.info("ML model prediction successful")

            return {
                '1': probs[0],
                'X': probs[1],
                '2': probs[2]
            }

        except FileNotFoundError:
            logger.warning("ML model not found, skipping ML method")
            return None
        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")
            return None

    def _prepare_ml_features(self) -> np.ndarray:
        """Prepare feature vector for ML model"""
        feature_order = [
            'home_form', 'away_form',
            'home_squad_quality', 'away_squad_quality',
            'home_motivation', 'away_motivation',
            'home_physical_condition', 'away_physical_condition',
            'home_field_advantage',
            'home_avg_goals', 'away_avg_goals',
            'home_avg_conceded', 'away_avg_conceded',
            'h2h_home_advantage',
            'rivalry_level'
        ]

        return np.array([[self.features.get(f, 0) for f in feature_order]])

    def _ensemble_predictions(
        self,
        scoring: Dict,
        poisson: Dict,
        ml: Optional[Dict] = None
    ) -> Dict:
        """
        Combine multiple prediction methods

        Uses weighted average with configurable weights
        """
        methods = [scoring, poisson]
        ensemble_weights = [0.4, 0.4]  # Scoring 40%, Poisson 40%

        if ml:
            methods.append(ml)
            ensemble_weights = [0.3, 0.3, 0.4]  # Scoring 30%, Poisson 30%, ML 40%
            logger.info("Using ML model in ensemble")

        # Weighted average
        prob_1 = sum(m['1'] * w for m, w in zip(methods, ensemble_weights))
        prob_X = sum(m['X'] * w for m, w in zip(methods, ensemble_weights))
        prob_2 = sum(m['2'] * w for m, w in zip(methods, ensemble_weights))

        # Final normalization
        total = prob_1 + prob_X + prob_2

        return {
            '1': round(prob_1 / total, 4),
            'X': round(prob_X / total, 4),
            '2': round(prob_2 / total, 4)
        }

    def _calculate_expected_goals(self, poisson_result: Dict = None) -> Dict:
        """
        Calculate expected goals from Poisson method

        Args:
            poisson_result: Pre-calculated Poisson results (to avoid recalculation)
        """
        if poisson_result is None:
            poisson_result = self._poisson_method()

        return {
            'home': round(poisson_result['_lambda_home'], 2),
            'away': round(poisson_result['_lambda_away'], 2)
        }

    def _most_likely_scoreline(self, expected_goals: Dict) -> str:
        """Find most probable scoreline"""
        lambda_home = expected_goals['home']
        lambda_away = expected_goals['away']

        max_prob = 0
        best_score = (1, 1)

        for h in range(6):
            for a in range(6):
                prob = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
                if prob > max_prob:
                    max_prob = prob
                    best_score = (h, a)

        return f"{best_score[0]}-{best_score[1]}"

    def _calculate_confidence(
        self,
        probabilities: Dict,
        scoring_probs: Dict = None,
        poisson_probs: Dict = None
    ) -> float:
        """
        Calculate prediction confidence

        Based on:
        - Data quality
        - Probability spread
        - Method agreement

        Args:
            probabilities: Final ensemble probabilities
            scoring_probs: Pre-calculated scoring method results (to avoid recalculation)
            poisson_probs: Pre-calculated Poisson method results (to avoid recalculation)
        """
        # 1. Data quality
        data_confidence = self.features.get('_meta', {}).get('overall_confidence', 0.7)

        # 2. Probability spread (clearer predictions = higher confidence)
        max_prob = max(probabilities.values())
        min_prob = min(probabilities.values())
        spread = max_prob - min_prob
        spread_confidence = min(spread * 0.8, 0.8)

        # 3. Method agreement (low divergence = higher confidence)
        if scoring_probs is None:
            scoring_probs = self._scoring_method()
        if poisson_probs is None:
            poisson_probs = self._poisson_method()

        divergence = sum(abs(scoring_probs[k] - poisson_probs[k]) for k in ['1', 'X', '2'])
        method_agreement = max(0, 1 - divergence)

        # Weighted combination
        final_confidence = (
            data_confidence * 0.40 +
            spread_confidence * 0.30 +
            method_agreement * 0.30
        )

        return round(final_confidence, 3)
