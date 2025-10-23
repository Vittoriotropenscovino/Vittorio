"""Data processor - transforms raw data into features"""

import logging
from typing import Dict, Optional
import numpy as np

from ..data_collection.fallback import (
    calculate_form_proxy,
    calculate_motivation_proxy,
    calculate_home_advantage_proxy,
)

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes raw collected data into features for prediction model

    Transforms data from DataCollectionOrchestrator into structured
    feature vectors suitable for ML models and statistical calculations.
    """

    def __init__(self, raw_data: Dict):
        """
        Initialize processor

        Args:
            raw_data: Raw data dict from DataCollectionOrchestrator
        """
        self.raw = raw_data
        self.features = {}

    def process(self) -> Dict:
        """
        Run complete processing pipeline

        Returns:
            Dict containing all processed features
        """
        logger.info("Starting data processing...")

        self.features = {
            **self._process_form(),
            **self._process_squad_quality(),
            **self._process_injuries(),
            **self._process_motivation(),
            **self._process_tactical(),
            **self._process_environmental(),
            **self._process_h2h(),
        }

        logger.info(f"Processed {len(self.features)} features")

        return self.features

    def _process_form(self) -> Dict:
        """Process team form features"""
        home_stats = self.raw.get('team_stats_home', {}).get('data', {})
        away_stats = self.raw.get('team_stats_away', {}).get('data', {})

        return {
            "home_form": home_stats.get('form', 5.0),
            "away_form": away_stats.get('form', 5.0),
            "home_avg_goals": home_stats.get('avg_goals_scored', 1.5),
            "away_avg_goals": away_stats.get('avg_goals_scored', 1.3),
            "home_avg_conceded": home_stats.get('avg_goals_conceded', 1.2),
            "away_avg_conceded": away_stats.get('avg_goals_conceded', 1.4),
            "home_avg_possession": home_stats.get('avg_possession', 50.0),
            "away_avg_possession": away_stats.get('avg_possession', 50.0),
        }

    def _process_squad_quality(self) -> Dict:
        """
        Process squad quality metrics

        Uses market value, squad depth, recent performance as proxies
        """
        home_stats = self.raw.get('team_stats_home', {}).get('data', {})
        away_stats = self.raw.get('team_stats_away', {}).get('data', {})

        # For now, use form and possession as proxy for quality
        # In full implementation, would use market values from Transfermarkt
        home_quality = min((
            home_stats.get('form', 5.0) +
            (home_stats.get('avg_possession', 50.0) / 10)
        ) / 2, 10.0)

        away_quality = min((
            away_stats.get('form', 5.0) +
            (away_stats.get('avg_possession', 50.0) / 10)
        ) / 2, 10.0)

        return {
            "home_squad_quality": round(home_quality, 1),
            "away_squad_quality": round(away_quality, 1),
        }

    def _process_injuries(self) -> Dict:
        """Process injury/availability impact"""
        home_injuries = self.raw.get('injuries_home', {}).get('data', []) or []
        away_injuries = self.raw.get('injuries_away', {}).get('data', []) or []

        # Calculate impact based on importance scores
        home_impact = sum(inj.get('importance', 5.0) for inj in home_injuries)
        away_impact = sum(inj.get('importance', 5.0) for inj in away_injuries)

        # Convert to physical condition score (10 = perfect)
        home_condition = max(10 - (home_impact * 0.5), 1.0)
        away_condition = max(10 - (away_impact * 0.5), 1.0)

        # Count key absences (importance >= 7)
        home_key_absences = len([i for i in home_injuries if i.get('importance', 0) >= 7])
        away_key_absences = len([i for i in away_injuries if i.get('importance', 0) >= 7])

        return {
            "home_physical_condition": round(home_condition, 1),
            "away_physical_condition": round(away_condition, 1),
            "home_key_absences": home_key_absences,
            "away_key_absences": away_key_absences,
            "home_total_absences": len(home_injuries),
            "away_total_absences": len(away_injuries),
        }

    def _process_motivation(self) -> Dict:
        """Process motivational factors"""
        standings = self.raw.get('standings', {}).get('data')

        if not standings:
            return {
                "home_motivation": 5.0,
                "away_motivation": 5.0,
                "is_rivalry": False,
                "rivalry_level": 0
            }

        home_pos = standings.get('home_position', 10)
        away_pos = standings.get('away_position', 10)
        home_points = standings.get('home_points', 30)
        away_points = standings.get('away_points', 30)

        # Calculate motivation scores
        home_motivation = calculate_motivation_proxy(home_pos, home_points)
        away_motivation = calculate_motivation_proxy(away_pos, away_points)

        # Check for rivalry (would query database in full implementation)
        is_rivalry = False
        rivalry_level = 0

        # Derby bonus (same city)
        # In full implementation, would check rivalry database

        return {
            "home_motivation": home_motivation,
            "away_motivation": away_motivation,
            "is_rivalry": is_rivalry,
            "rivalry_level": rivalry_level,
            "home_position": home_pos,
            "away_position": away_pos,
        }

    def _process_tactical(self) -> Dict:
        """Process tactical matchup"""
        home_stats = self.raw.get('team_stats_home', {}).get('data', {})
        away_stats = self.raw.get('team_stats_away', {}).get('data', {})

        home_possession = home_stats.get('avg_possession', 50.0)
        away_possession = away_stats.get('avg_possession', 50.0)

        # Tactical matchup score
        # Positive = home advantage, Negative = away advantage
        possession_diff = home_possession - away_possession

        # Normalize to -1 to 1 range
        tactical_advantage = np.clip(possession_diff / 25.0, -1.0, 1.0)

        return {
            "home_possession_style": home_possession,
            "away_possession_style": away_possession,
            "tactical_matchup_score": round(tactical_advantage, 2),
        }

    def _process_environmental(self) -> Dict:
        """Process environmental factors (weather, home advantage)"""
        weather = self.raw.get('weather', {}).get('data')

        # Home field advantage
        home_advantage = 6.0  # Base home advantage

        # Weather impact
        weather_penalty = 0
        if weather:
            conditions = weather.get('conditions', '')
            if conditions in ['Rain', 'Snow', 'Thunderstorm']:
                weather_penalty += 0.5
            if weather.get('wind_speed', 0) > 30:  # km/h
                weather_penalty += 0.3

        final_home_advantage = max(home_advantage - weather_penalty, 1.0)

        weather_data = {
            "home_field_advantage": round(final_home_advantage, 1),
            "weather_impact": round(weather_penalty, 1),
        }

        if weather:
            weather_data.update({
                "temperature": weather.get('temperature', 20),
                "precipitation_probability": weather.get('precipitation_prob', 0),
                "wind_speed": weather.get('wind_speed', 0),
                "conditions": weather.get('conditions', 'Clear'),
            })

        return weather_data

    def _process_h2h(self) -> Dict:
        """Process head-to-head history"""
        h2h = self.raw.get('h2h', {}).get('data')

        if not h2h:
            return {
                "h2h_home_advantage": 0,
                "h2h_matches": 0,
                "h2h_avg_goals": 2.5,
            }

        home_win_rate = h2h.get('home_win_pct', 0.33)

        # Psychological factor from H2H dominance
        psychological_factor = 0
        if home_win_rate > 0.6:
            psychological_factor = 0.5
        elif home_win_rate < 0.2:
            psychological_factor = -0.5

        avg_total_goals = (
            h2h.get('avg_home_goals', 1.5) +
            h2h.get('avg_away_goals', 1.2)
        )

        return {
            "h2h_home_advantage": round(psychological_factor, 1),
            "h2h_matches": h2h.get('matches_played', 0),
            "h2h_avg_goals": round(avg_total_goals, 2),
            "h2h_home_win_pct": round(home_win_rate, 3),
        }

    def get_feature_vector(self, feature_order: list = None) -> np.ndarray:
        """
        Get features as numpy array for ML models

        Args:
            feature_order: List of feature names in specific order

        Returns:
            Numpy array of feature values
        """
        if feature_order is None:
            feature_order = self._get_default_feature_order()

        return np.array([self.features.get(f, 0) for f in feature_order])

    def _get_default_feature_order(self) -> list:
        """Default feature order for ML models"""
        return [
            'home_form', 'away_form',
            'home_squad_quality', 'away_squad_quality',
            'home_motivation', 'away_motivation',
            'home_physical_condition', 'away_physical_condition',
            'home_field_advantage',
            'home_avg_goals', 'away_avg_goals',
            'home_avg_conceded', 'away_avg_conceded',
            'h2h_home_advantage',
            'rivalry_level',
        ]

    def get_summary(self) -> Dict:
        """Get summary of processed features"""
        return {
            "total_features": len(self.features),
            "feature_categories": {
                "form": len([k for k in self.features if 'form' in k]),
                "quality": len([k for k in self.features if 'quality' in k]),
                "injuries": len([k for k in self.features if 'condition' in k or 'absence' in k]),
                "motivation": len([k for k in self.features if 'motivation' in k]),
                "tactical": len([k for k in self.features if 'tactical' in k or 'possession' in k]),
                "environmental": len([k for k in self.features if 'weather' in k or 'field' in k]),
                "h2h": len([k for k in self.features if 'h2h' in k]),
            },
            "key_insights": self._get_key_insights()
        }

    def _get_key_insights(self) -> Dict:
        """Extract key insights from features"""
        insights = {}

        # Form comparison
        form_diff = self.features.get('home_form', 5) - self.features.get('away_form', 5)
        if abs(form_diff) > 2:
            insights['form'] = f"{'Home' if form_diff > 0 else 'Away'} team in significantly better form"

        # Injury impact
        if self.features.get('home_key_absences', 0) >= 3:
            insights['injuries'] = "Home team missing multiple key players"
        elif self.features.get('away_key_absences', 0) >= 3:
            insights['injuries'] = "Away team missing multiple key players"

        # Motivation gap
        motiv_diff = self.features.get('home_motivation', 5) - self.features.get('away_motivation', 5)
        if abs(motiv_diff) > 2:
            insights['motivation'] = f"{'Home' if motiv_diff > 0 else 'Away'} team more motivated"

        return insights
