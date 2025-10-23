"""Supplementary calculations - Over/Under, BTTS, correct scores"""

import logging
import numpy as np
from scipy.stats import poisson
from typing import Dict, List

logger = logging.getLogger(__name__)


class SupplementaryCalculations:
    """Calculate supplementary betting markets"""

    def __init__(self, expected_goals: Dict, probabilities: Dict):
        """
        Initialize with base prediction data

        Args:
            expected_goals: {'home': float, 'away': float}
            probabilities: {'1': float, 'X': float, '2': float}
        """
        self.xg = expected_goals
        self.probs = probabilities

    def calculate_all(self) -> Dict:
        """Calculate all supplementary markets"""
        return {
            "over_under": self._over_under(),
            "btts": self._both_teams_to_score(),
            "clean_sheet": self._clean_sheet_probability(),
            "correct_score_top5": self._top_correct_scores(),
            "goal_ranges": self._goal_ranges(),
            "asian_handicap": self._asian_handicap(),
        }

    def _over_under(self, lines: List[float] = [0.5, 1.5, 2.5, 3.5, 4.5]) -> Dict:
        """
        Calculate Over/Under probabilities for multiple lines

        Args:
            lines: Goal lines to calculate (default: 0.5, 1.5, 2.5, 3.5, 4.5)
        """
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        results = {}

        for line in lines:
            prob_under = 0
            prob_over = 0

            # Sum probabilities for all scorelines
            for home_goals in range(10):
                for away_goals in range(10):
                    prob = poisson.pmf(home_goals, lambda_home) * poisson.pmf(away_goals, lambda_away)
                    total_goals = home_goals + away_goals

                    if total_goals < line:
                        prob_under += prob
                    else:
                        prob_over += prob

            results[f"under_{line}"] = round(prob_under, 4)
            results[f"over_{line}"] = round(prob_over, 4)

        return results

    def _both_teams_to_score(self) -> Dict:
        """Probability both teams score (BTTS)"""
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        # P(Home > 0) * P(Away > 0)
        prob_home_scores = 1 - poisson.pmf(0, lambda_home)
        prob_away_scores = 1 - poisson.pmf(0, lambda_away)

        prob_btts_yes = prob_home_scores * prob_away_scores
        prob_btts_no = 1 - prob_btts_yes

        return {
            "btts_yes": round(prob_btts_yes, 4),
            "btts_no": round(prob_btts_no, 4)
        }

    def _clean_sheet_probability(self) -> Dict:
        """Probability of clean sheet for each team"""
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        return {
            "home_clean_sheet": round(poisson.pmf(0, lambda_away), 4),
            "away_clean_sheet": round(poisson.pmf(0, lambda_home), 4)
        }

    def _top_correct_scores(self, top_n: int = 10) -> List[Dict]:
        """
        Top N most likely correct scores

        Args:
            top_n: Number of top scores to return
        """
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        scores = []

        for h in range(7):  # 0-6 goals
            for a in range(7):
                prob = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
                scores.append({
                    "score": f"{h}-{a}",
                    "probability": round(prob, 5)
                })

        # Sort by probability
        scores.sort(key=lambda x: x['probability'], reverse=True)

        return scores[:top_n]

    def _goal_ranges(self) -> Dict:
        """Probability of total goals falling in ranges"""
        lambda_total = self.xg['home'] + self.xg['away']

        ranges = {
            "0-1": sum(poisson.pmf(g, lambda_total) for g in range(2)),
            "2-3": sum(poisson.pmf(g, lambda_total) for g in range(2, 4)),
            "4-5": sum(poisson.pmf(g, lambda_total) for g in range(4, 6)),
            "6+": 1 - sum(poisson.pmf(g, lambda_total) for g in range(6))
        }

        return {k: round(v, 4) for k, v in ranges.items()}

    def _asian_handicap(self, handicaps: List[float] = [-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5]) -> Dict:
        """
        Asian Handicap probabilities

        Args:
            handicaps: Handicap lines (negative = home handicap, positive = away handicap)
        """
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        results = {}

        for handicap in handicaps:
            prob_home_wins = 0
            prob_draw = 0
            prob_away_wins = 0

            for h in range(10):
                for a in range(10):
                    prob = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)

                    # Apply handicap to home team
                    adjusted_home = h + handicap

                    if adjusted_home > a:
                        prob_home_wins += prob
                    elif adjusted_home == a:
                        prob_draw += prob
                    else:
                        prob_away_wins += prob

            key = f"ah_{handicap:+.1f}".replace('.', '_')
            results[key] = {
                "home_wins": round(prob_home_wins, 4),
                "draw": round(prob_draw, 4),
                "away_wins": round(prob_away_wins, 4)
            }

        return results

    def _halftime_fulltime(self) -> Dict:
        """
        Half-time/Full-time probabilities

        Simplified model: assumes HT score is ~45% of FT score
        """
        lambda_home_ht = self.xg['home'] * 0.45
        lambda_away_ht = self.xg['away'] * 0.45
        lambda_home_ft = self.xg['home']
        lambda_away_ft = self.xg['away']

        # Calculate main HT/FT combinations
        ht_ft_probs = {}

        for ht_result in ['1', 'X', '2']:
            for ft_result in ['1', 'X', '2']:
                # Simplified probability calculation
                # This would need more sophisticated modeling in production
                key = f"{ht_result}/{ft_result}"
                ht_ft_probs[key] = 0.0

        # Most common patterns
        ht_ft_probs['1/1'] = self.probs['1'] * 0.6  # Home leads at HT and wins
        ht_ft_probs['X/1'] = self.probs['1'] * 0.25  # Draw at HT, home wins
        ht_ft_probs['2/2'] = self.probs['2'] * 0.6  # Away leads at HT and wins
        ht_ft_probs['X/2'] = self.probs['2'] * 0.25  # Draw at HT, away wins
        ht_ft_probs['X/X'] = self.probs['X'] * 0.5  # Draw at HT and FT

        # Fill remaining to sum to 1.0
        total_assigned = sum(ht_ft_probs.values())
        remaining = 1.0 - total_assigned

        # Distribute remaining probability to other combinations
        other_combinations = ['1/X', '1/2', '2/1', '2/X', 'X/1', 'X/2']
        for combo in other_combinations:
            if combo not in ht_ft_probs or ht_ft_probs[combo] == 0:
                ht_ft_probs[combo] = remaining / len(other_combinations)

        return {k: round(v, 4) for k, v in ht_ft_probs.items()}

    def _team_to_score_first(self) -> Dict:
        """Probability each team scores first"""
        lambda_home = self.xg['home']
        lambda_away = self.xg['away']

        # Simplified model based on scoring rates
        total_rate = lambda_home + lambda_away

        if total_rate == 0:
            return {
                "home_scores_first": 0.5,
                "away_scores_first": 0.5,
                "no_goals": 0.0
            }

        prob_no_goals = poisson.pmf(0, lambda_home) * poisson.pmf(0, lambda_away)

        # Probability home scores first (given at least one goal)
        prob_home_first = (lambda_home / total_rate) * (1 - prob_no_goals)
        prob_away_first = (lambda_away / total_rate) * (1 - prob_no_goals)

        return {
            "home_scores_first": round(prob_home_first, 4),
            "away_scores_first": round(prob_away_first, 4),
            "no_goals": round(prob_no_goals, 4)
        }
