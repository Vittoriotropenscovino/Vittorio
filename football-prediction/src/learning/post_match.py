"""Post-match analysis and learning system"""

import logging
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PostMatchAnalyzer:
    """
    Analyze prediction accuracy after match completion

    Calculates metrics and updates model performance tracking
    """

    def __init__(self, prediction_id: int, db_session=None):
        """
        Initialize analyzer

        Args:
            prediction_id: ID of prediction to analyze
            db_session: Database session (optional)
        """
        self.prediction_id = prediction_id
        self.db = db_session

        # Load prediction and match data
        self.prediction = self._load_prediction()
        self.match = self._load_match()

    def _load_prediction(self):
        """Load prediction from database"""
        if not self.db:
            from database import get_db
            with get_db() as db:
                from database.models import Prediction
                return db.query(Prediction).get(self.prediction_id)
        else:
            from database.models import Prediction
            return self.db.query(Prediction).get(self.prediction_id)

    def _load_match(self):
        """Load match data"""
        if not self.db:
            from database import get_db
            with get_db() as db:
                from database.models import Match
                return db.query(Match).get(self.prediction.match_id)
        else:
            from database.models import Match
            return self.db.query(Match).get(self.prediction.match_id)

    def analyze(self) -> Dict:
        """
        Complete post-match analysis

        Returns:
            Dict with accuracy metrics and insights
        """
        if self.match.status != 'FT':
            raise ValueError(f"Match not finished yet (status: {self.match.status})")

        logger.info(f"Analyzing prediction {self.prediction_id} for match {self.match.id}")

        results = {
            "prediction_accuracy": self._check_prediction_accuracy(),
            "probability_calibration": self._calculate_brier_score(),
            "log_loss": self._calculate_log_loss(),
            "supplementary_accuracy": self._check_supplementary_markets(),
        }

        # Save results to database
        self._save_results(results)

        logger.info(
            f"Analysis complete: "
            f"{'✅ Correct' if results['prediction_accuracy']['correct'] else '❌ Incorrect'} "
            f"(Brier: {results['probability_calibration']:.4f})"
        )

        return results

    def _check_prediction_accuracy(self) -> Dict:
        """Check if prediction was correct"""
        actual_home = self.match.home_score
        actual_away = self.match.away_score

        # Determine actual result
        if actual_home > actual_away:
            actual_result = '1'
        elif actual_home < actual_away:
            actual_result = '2'
        else:
            actual_result = 'X'

        # Predicted result (highest probability)
        predicted_result = self.prediction.predicted_result

        # Check correctness
        correct = actual_result == predicted_result

        # Get probability assigned to actual outcome
        prob_actual = {
            '1': self.prediction.prob_home,
            'X': self.prediction.prob_draw,
            '2': self.prediction.prob_away
        }[actual_result]

        return {
            "predicted": predicted_result,
            "actual": actual_result,
            "correct": correct,
            "predicted_probability": float(prob_actual),
            "actual_score": f"{actual_home}-{actual_away}",
            "predicted_score": self.prediction.predicted_score,
            "correct_score": self.prediction.predicted_score == f"{actual_home}-{actual_away}"
        }

    def _calculate_brier_score(self) -> float:
        """
        Calculate Brier score

        Brier score measures probability accuracy
        0 = perfect, 1 = worst possible
        """
        actual_home = self.match.home_score
        actual_away = self.match.away_score

        # One-hot encoding of actual result
        if actual_home > actual_away:
            actual_vector = [1, 0, 0]  # Home win
        elif actual_home < actual_away:
            actual_vector = [0, 0, 1]  # Away win
        else:
            actual_vector = [0, 1, 0]  # Draw

        # Predicted probabilities
        predicted_vector = [
            float(self.prediction.prob_home),
            float(self.prediction.prob_draw),
            float(self.prediction.prob_away)
        ]

        # Brier score formula
        brier = sum((actual_vector[i] - predicted_vector[i])**2 for i in range(3)) / 3

        return round(brier, 4)

    def _calculate_log_loss(self) -> float:
        """
        Calculate logarithmic loss

        Penalizes confident wrong predictions heavily
        """
        actual_home = self.match.home_score
        actual_away = self.match.away_score

        # Determine actual result
        if actual_home > actual_away:
            actual_result = '1'
        elif actual_home < actual_away:
            actual_result = '2'
        else:
            actual_result = 'X'

        # Get probability of actual outcome
        prob_actual = {
            '1': float(self.prediction.prob_home),
            'X': float(self.prediction.prob_draw),
            '2': float(self.prediction.prob_away)
        }[actual_result]

        # Clip to avoid log(0)
        prob_actual = max(min(prob_actual, 0.9999), 0.0001)

        # Log loss
        log_loss = -np.log(prob_actual)

        return round(log_loss, 4)

    def _check_supplementary_markets(self) -> Dict:
        """Check accuracy of supplementary predictions"""
        actual_home = self.match.home_score
        actual_away = self.match.away_score
        actual_total = actual_home + actual_away

        results = {}

        # Over/Under 2.5
        if self.prediction.prob_over_2_5 is not None:
            actual_over_2_5 = actual_total > 2.5
            predicted_over_2_5 = self.prediction.prob_over_2_5 > 0.5
            results['over_2_5_correct'] = actual_over_2_5 == predicted_over_2_5

        # BTTS
        if self.prediction.prob_btts_yes is not None:
            actual_btts = actual_home > 0 and actual_away > 0
            predicted_btts = self.prediction.prob_btts_yes > 0.5
            results['btts_correct'] = actual_btts == predicted_btts

        # Clean sheets
        results['home_clean_sheet_actual'] = actual_away == 0
        results['away_clean_sheet_actual'] = actual_home == 0

        return results

    def _save_results(self, results: Dict):
        """Save analysis results to database"""
        if not self.db:
            from database import get_db
            with get_db() as db:
                self._do_save(db, results)
        else:
            self._do_save(self.db, results)

    def _do_save(self, db, results: Dict):
        """Perform actual database save"""
        from database.models import PredictionResult

        # Check if result already exists
        existing = db.query(PredictionResult).filter_by(
            prediction_id=self.prediction_id
        ).first()

        if existing:
            logger.warning(f"Result already exists for prediction {self.prediction_id}, updating...")
            result_record = existing
        else:
            result_record = PredictionResult(prediction_id=self.prediction_id)

        # Update fields
        acc = results['prediction_accuracy']
        result_record.actual_result = acc['actual']
        result_record.actual_score = acc['actual_score']
        result_record.predicted_result = acc['predicted']
        result_record.correct_result = acc['correct']
        result_record.correct_score = acc.get('correct_score', False)
        result_record.probability_assigned_to_actual = acc['predicted_probability']
        result_record.brier_score = results['probability_calibration']
        result_record.log_loss = results.get('log_loss')

        # Supplementary
        supp = results.get('supplementary_accuracy', {})
        result_record.over_2_5_correct = supp.get('over_2_5_correct')
        result_record.btts_correct = supp.get('btts_correct')

        # Calculate simulated ROI (if we bet 1 unit)
        if acc['correct']:
            # If correct, calculate profit based on implied odds
            prob = acc['predicted_probability']
            fair_odds = 1 / prob
            result_record.simulated_roi = fair_odds - 1  # Profit
        else:
            result_record.simulated_roi = -1.0  # Loss of 1 unit

        if not existing:
            db.add(result_record)

        db.commit()

        logger.info(f"Saved analysis results for prediction {self.prediction_id}")


def analyze_model_performance(last_n_predictions: int = 100) -> Dict:
    """
    Analyze overall model performance

    Args:
        last_n_predictions: Number of recent predictions to analyze

    Returns:
        Dict with performance metrics
    """
    from database import get_db

    with get_db() as db:
        from database.models import PredictionResult

        # Get last N results
        results = db.query(PredictionResult).order_by(
            PredictionResult.created_at.desc()
        ).limit(last_n_predictions).all()

        if not results:
            logger.warning("No prediction results available")
            return {
                "error": "No data available",
                "sample_size": 0
            }

        total = len(results)

        # Calculate metrics
        correct = sum(1 for r in results if r.correct_result)
        accuracy = correct / total

        avg_brier = np.mean([r.brier_score for r in results if r.brier_score is not None])

        avg_log_loss = np.mean([r.log_loss for r in results if r.log_loss is not None])

        # ROI simulation
        roi_values = [r.simulated_roi for r in results if r.simulated_roi is not None]
        avg_roi = np.mean(roi_values) if roi_values else 0

        # Accuracy by predicted outcome
        by_outcome = {}
        for outcome in ['1', 'X', '2']:
            outcome_results = [r for r in results if r.predicted_result == outcome]
            if outcome_results:
                outcome_correct = sum(1 for r in outcome_results if r.correct_result)
                by_outcome[outcome] = {
                    "count": len(outcome_results),
                    "accuracy": outcome_correct / len(outcome_results)
                }

        performance = {
            "sample_size": total,
            "overall_accuracy": round(accuracy, 4),
            "avg_brier_score": round(avg_brier, 4),
            "avg_log_loss": round(avg_log_loss, 4) if avg_log_loss else None,
            "simulated_roi": round(avg_roi, 4),
            "accuracy_by_outcome": by_outcome,
            "total_profit_units": round(sum(roi_values), 2) if roi_values else 0
        }

        logger.info(
            f"Model Performance (n={total}): "
            f"Accuracy={accuracy:.1%}, Brier={avg_brier:.4f}, ROI={avg_roi:.2%}"
        )

        return performance
