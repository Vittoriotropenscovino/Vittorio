"""Prediction validator - Quality assurance and sanity checks"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class PredictionValidator:
    """
    Validates predictions for quality and logical consistency

    Performs multiple checks:
    - Probability constraints
    - Logical consistency
    - Market alignment
    - Data quality thresholds
    """

    def __init__(self, prediction: Dict, features: Dict):
        """
        Initialize validator

        Args:
            prediction: Prediction dict from PredictionModel
            features: Features dict from DataProcessor
        """
        self.prediction = prediction
        self.features = features
        self.warnings = []
        self.errors = []

    def validate(self) -> Dict:
        """
        Run all validation checks

        Returns:
            Dict with validation results and confidence adjustment
        """
        logger.info("Running prediction validation...")

        checks = [
            self._check_probability_sum(),
            self._check_probability_ranges(),
            self._check_draw_probability(),
            self._check_logical_consistency(),
            self._check_data_quality(),
        ]

        passed = all(checks)

        # Calculate confidence adjustment based on warnings/errors
        adjustment = self._calculate_adjustment()

        result = {
            "validation_passed": passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "final_confidence_adjustment": adjustment,
            "checks_passed": sum(checks),
            "total_checks": len(checks)
        }

        if not passed:
            logger.warning(f"Validation failed: {len(self.errors)} errors")
        else:
            logger.info(f"Validation passed with {len(self.warnings)} warnings")

        return result

    def _check_probability_sum(self) -> bool:
        """Check that probabilities sum to 1.0"""
        probs = self.prediction['probabilities']
        total = probs['1'] + probs['X'] + probs['2']

        if abs(total - 1.0) > 0.01:
            self.errors.append(
                f"Probability sum = {total:.4f} (should be 1.0)"
            )
            return False

        return True

    def _check_probability_ranges(self) -> bool:
        """Check each probability is between 0 and 1"""
        probs = self.prediction['probabilities']

        for outcome, prob in probs.items():
            if not (0 <= prob <= 1):
                self.errors.append(
                    f"Probability {outcome} = {prob} out of range [0,1]"
                )
                return False

        return True

    def _check_draw_probability(self) -> bool:
        """Check draw probability is in realistic range"""
        prob_draw = self.prediction['probabilities']['X']

        if not (0.05 <= prob_draw <= 0.50):
            self.warnings.append(
                f"Draw probability {prob_draw:.1%} unusual (expected 5-50%)"
            )
            return False

        return True

    def _check_logical_consistency(self) -> bool:
        """
        Check predictions make logical sense given features

        Examples:
        - Strong home team vs weak away team should favor home
        - Team with many injuries should be disadvantaged
        - Derby matches should have higher draw probability
        """
        probs = self.prediction['probabilities']
        features = self.features

        all_consistent = True

        # Check 1: Top team at home vs bottom team
        home_position = features.get('home_position', 10)
        away_position = features.get('away_position', 10)

        if home_position <= 4 and away_position >= 18:
            # Home is top 4, away is relegation zone
            if probs['1'] < 0.40:
                self.warnings.append(
                    "Top team at home vs relegation zone: "
                    "unexpectedly low home win probability"
                )
                all_consistent = False

        # Check 2: High-intensity rivalry
        if features.get('is_rivalry') and features.get('rivalry_level', 0) >= 8:
            if probs['X'] < 0.20:
                self.warnings.append(
                    "High-intensity rivalry: draw probability seems low"
                )
                all_consistent = False

        # Check 3: Team with many key absences
        if features.get('home_key_absences', 0) >= 5:
            if probs['1'] > 0.50:
                self.warnings.append(
                    "Home team has 5+ key absences but still heavily favored"
                )
                all_consistent = False

        if features.get('away_key_absences', 0) >= 5:
            if probs['2'] > 0.50:
                self.warnings.append(
                    "Away team has 5+ key absences but still heavily favored"
                )
                all_consistent = False

        # Check 4: Form mismatch
        form_diff = features.get('home_form', 5) - features.get('away_form', 5)

        if form_diff > 3:  # Home in much better form
            if probs['1'] < probs['2']:
                self.warnings.append(
                    f"Home team in much better form ({form_diff:+.1f}) "
                    "but away team favored"
                )
                all_consistent = False

        elif form_diff < -3:  # Away in much better form
            if probs['2'] < probs['1']:
                self.warnings.append(
                    f"Away team in much better form ({-form_diff:+.1f}) "
                    "but home team favored"
                )
                all_consistent = False

        return all_consistent

    def _check_data_quality(self) -> bool:
        """
        Check input data quality is sufficient

        Aborts prediction if quality too low
        """
        meta = self.features.get('_meta', {})
        missing = meta.get('missing_data', [])

        # Critical data sources
        critical_data = [
            'team_stats_home',
            'team_stats_away',
            'fixture_data'
        ]

        missing_critical = [d for d in missing if d in critical_data]

        if missing_critical:
            self.warnings.append(
                f"Critical data missing: {', '.join(missing_critical)}"
            )

        # Overall confidence check
        overall_confidence = meta.get('overall_confidence', 0)

        if overall_confidence < 0.50:
            self.errors.append(
                f"Data quality too low ({overall_confidence:.1%}) - "
                "prediction unreliable"
            )
            return False

        if overall_confidence < 0.70:
            self.warnings.append(
                f"Data quality moderate ({overall_confidence:.1%})"
            )

        return True

    def _check_market_alignment(self, market_odds: Dict = None) -> bool:
        """
        Check alignment with betting market (if odds available)

        Large divergence might indicate:
        - Model issue
        - Value bet opportunity
        - Missing information
        """
        if not market_odds:
            # No odds data available
            return True

        probs = self.prediction['probabilities']

        for outcome in ['1', 'X', '2']:
            our_prob = probs[outcome]
            market_prob = market_odds.get(f'implied_prob_{outcome}')

            if not market_prob:
                continue

            divergence = abs(our_prob - market_prob)

            if divergence > 0.20:
                self.warnings.append(
                    f"Large divergence on {outcome}: "
                    f"us {our_prob:.1%} vs market {market_prob:.1%}"
                )

        return True

    def _calculate_adjustment(self) -> float:
        """
        Calculate confidence adjustment based on validation results

        Returns:
            Multiplier for final confidence (0.0 to 1.0)
        """
        if self.errors:
            # Critical errors: max 50% confidence
            return 0.50

        # Penalty for warnings
        warning_penalty = len(self.warnings) * 0.05

        # Minimum 60% of original confidence
        return max(1.0 - warning_penalty, 0.60)

    def get_quality_label(self, adjusted_confidence: float) -> str:
        """
        Get quality label for prediction

        Args:
            adjusted_confidence: Final confidence after adjustments

        Returns:
            'HIGH', 'MEDIUM', or 'LOW'
        """
        if adjusted_confidence >= 0.75:
            return 'HIGH'
        elif adjusted_confidence >= 0.60:
            return 'MEDIUM'
        else:
            return 'LOW'
