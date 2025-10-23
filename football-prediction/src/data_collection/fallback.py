"""Fallback and proxy calculation systems"""

import logging
from typing import Callable, List, Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DataUnavailableError(Exception):
    """Raised when all data sources fail"""
    pass


@dataclass
class DataSource:
    """Configuration for a data source"""
    name: str
    fetcher: Callable
    confidence: float  # 0.0 to 1.0
    timeout: int = 10


class WaterfallFetcher:
    """
    Waterfall system for data fetching with automatic fallback

    Tries data sources in order of confidence, falling back to next source if one fails.
    """

    def __init__(self, sources: List[DataSource]):
        """
        Initialize waterfall fetcher

        Args:
            sources: List of DataSource objects
        """
        # Sort sources by confidence (highest first)
        self.sources = sorted(sources, key=lambda x: x.confidence, reverse=True)

    def fetch(self, **kwargs) -> Dict:
        """
        Fetch data with automatic fallback

        Args:
            **kwargs: Arguments to pass to fetcher functions

        Returns:
            Dict containing:
                - data: The fetched data
                - source: Name of successful source
                - confidence: Confidence score of source
                - fallback_used: Whether fallback was needed

        Raises:
            DataUnavailableError: If all sources fail
        """
        errors = []
        fallback_used = False

        for i, source in enumerate(self.sources):
            if i > 0:
                fallback_used = True

            try:
                logger.info(f"Trying data source: {source.name}")

                result = source.fetcher(**kwargs)

                logger.info(f"✓ Data source {source.name} succeeded")

                return {
                    "data": result,
                    "source": source.name,
                    "confidence": source.confidence,
                    "fallback_used": fallback_used
                }

            except Exception as e:
                error_msg = f"{source.name}: {str(e)}"
                logger.warning(f"✗ Data source {source.name} failed: {e}")
                errors.append(error_msg)
                continue

        # All sources failed
        raise DataUnavailableError(
            f"All data sources failed. Errors: {'; '.join(errors)}"
        )


def calculate_xg_proxy(team_stats: Dict) -> float:
    """
    Calculate proxy xG when actual xG data is unavailable

    Uses empirical formula based on historical correlation between
    shot metrics and expected goals.

    Args:
        team_stats: Dict containing:
            - shots_on_target: Number of shots on target
            - shots_off_target: Number of shots off target
            - big_chances_created: Number of big chances (optional)

    Returns:
        Estimated xG value
    """
    shots_on_target = team_stats.get('shots_on_target', 0)
    shots_off_target = team_stats.get('shots_off_target', 0)
    big_chances = team_stats.get('big_chances_created', 0)

    # Empirical conversion rates based on statistical analysis
    # Shot on target ~ 11% conversion
    # Shot off target ~ 2% conversion
    # Big chance ~ 35% conversion

    xg_proxy = (
        shots_on_target * 0.11 +
        shots_off_target * 0.02 +
        big_chances * 0.35
    )

    return round(xg_proxy, 2)


def calculate_importance_proxy(player: Dict, team_stats: Dict) -> float:
    """
    Calculate player importance score (1-10) when detailed data unavailable

    Uses combination of:
    - Minutes played
    - Goal/assist contributions
    - Market value (relative to team)
    - Average rating
    - Position bonus

    Args:
        player: Dict containing:
            - minutes: Minutes played
            - goals: Goals scored
            - assists: Assists
            - appearances: Number of appearances
            - market_value: Market value in currency
            - average_rating: Average match rating
            - position: Player position
        team_stats: Dict containing:
            - total_matches: Team's total matches
            - highest_value: Highest player value in team

    Returns:
        Importance score from 1.0 to 10.0
    """
    # 1. Minutes played score (max 3.0 points)
    minutes_played = player.get('minutes', 0)
    total_possible_minutes = team_stats.get('total_matches', 1) * 90
    minutes_score = (minutes_played / max(total_possible_minutes, 1)) * 3.0

    # 2. Goal/assist contribution score (max 2.0 points)
    goals = player.get('goals', 0)
    assists = player.get('assists', 0)
    appearances = max(player.get('appearances', 1), 1)
    contribution_per_match = (goals + assists) / appearances
    contribution_score = min(contribution_per_match * 2.0, 2.0)

    # 3. Market value score (max 2.5 points)
    player_value = player.get('market_value', 0)
    max_team_value = max(team_stats.get('highest_value', 1), 1)
    value_score = (player_value / max_team_value) * 2.5

    # 4. Rating score (max 2.0 points)
    # Assuming ratings are on 1-10 scale, typically 5-9
    avg_rating = player.get('average_rating', 6.5)
    rating_score = max((avg_rating - 5.0) / 2.0, 0)  # Normalize to 0-2

    # 5. Position bonus (max 0.7 points)
    position = player.get('position', 'Unknown')
    position_bonus = {
        'Goalkeeper': 0.5,
        'Defender': 0.3,
        'Midfielder': 0.5,
        'Forward': 0.7,
        'Attacker': 0.7,
    }.get(position, 0.3)

    # Calculate total importance
    importance = (
        minutes_score +
        contribution_score +
        value_score +
        rating_score +
        position_bonus
    )

    # Clamp to 1.0-10.0 range
    return round(min(max(importance, 1.0), 10.0), 1)


def calculate_form_proxy(results: List[str]) -> float:
    """
    Calculate form score from recent results

    Args:
        results: List of recent results ('W', 'D', 'L')

    Returns:
        Form score from 1.0 to 10.0
    """
    if not results:
        return 5.0

    # Convert results to points
    points_map = {'W': 3, 'D': 1, 'L': 0}
    points = [points_map.get(r.upper(), 0) for r in results]

    # Calculate average points per game
    avg_points = sum(points) / len(points)

    # Convert to 1-10 scale
    # 0 points/game = 1.0, 3 points/game = 10.0
    form_score = (avg_points / 3.0) * 9.0 + 1.0

    return round(form_score, 1)


def calculate_motivation_proxy(
    position: int,
    points: int,
    total_teams: int = 20
) -> float:
    """
    Calculate motivation score based on league position

    Args:
        position: Current league position
        points: Current points
        total_teams: Total teams in league

    Returns:
        Motivation score from 1.0 to 10.0
    """
    # Top positions: Fighting for Champions League/title
    if position <= 4:
        return round(8.0 + (4 - position) * 0.5, 1)

    # Europa League spots
    elif position <= 7:
        return 7.0

    # Mid-table: Lower motivation
    elif position <= total_teams - 6:
        return 5.0

    # Relegation battle: High motivation
    else:
        distance_from_bottom = total_teams - position
        return round(7.0 + distance_from_bottom * 0.3, 1)


def calculate_home_advantage_proxy(
    stadium_capacity: int,
    avg_attendance_pct: float,
    recent_home_record: List[str] = None
) -> float:
    """
    Calculate home advantage factor

    Args:
        stadium_capacity: Stadium capacity
        avg_attendance_pct: Average attendance as percentage (0.0-1.0)
        recent_home_record: Recent home results ['W', 'D', 'L']

    Returns:
        Home advantage score from 1.0 to 10.0
    """
    base_score = 5.0

    # Attendance boost (max +2.5)
    attendance_boost = avg_attendance_pct * 2.5

    # Stadium size factor (larger = more intimidating, max +1.0)
    if stadium_capacity > 60000:
        size_boost = 1.0
    elif stadium_capacity > 40000:
        size_boost = 0.7
    elif stadium_capacity > 25000:
        size_boost = 0.5
    else:
        size_boost = 0.3

    # Recent home form boost (max +1.5)
    form_boost = 0
    if recent_home_record:
        home_wins = recent_home_record.count('W')
        form_boost = (home_wins / len(recent_home_record)) * 1.5

    total = base_score + attendance_boost + size_boost + form_boost

    return round(min(total, 10.0), 1)


def calculate_tactical_matchup_score(
    team_a_possession: float,
    team_b_possession: float,
    team_a_press_intensity: float = None,
    team_b_press_intensity: float = None
) -> float:
    """
    Calculate tactical matchup advantage

    Args:
        team_a_possession: Team A average possession %
        team_b_possession: Team B average possession %
        team_a_press_intensity: Team A pressing intensity (optional)
        team_b_press_intensity: Team B pressing intensity (optional)

    Returns:
        Score from -1.0 (Team B advantage) to +1.0 (Team A advantage)
    """
    # Possession mismatch
    possession_diff = team_a_possession - team_b_possession

    # Normalize to -1 to 1 range
    tactical_score = possession_diff / 50.0

    # Pressing intensity mismatch (if available)
    if team_a_press_intensity is not None and team_b_press_intensity is not None:
        press_diff = (team_a_press_intensity - team_b_press_intensity) / 100.0
        tactical_score = (tactical_score + press_diff) / 2.0

    # Clamp to -1.0 to 1.0
    return round(max(min(tactical_score, 1.0), -1.0), 2)


# Example usage of WaterfallFetcher
def example_xg_fetcher_with_fallback():
    """Example of setting up xG fetching with fallback"""

    def fetch_from_understat(team_id: int):
        from .scrapers import UnderstatScraper
        scraper = UnderstatScraper()
        return scraper.scrape_team_xg(team_id=team_id)

    def fetch_from_fbref(team_id: int):
        from .scrapers import FBrefScraper
        scraper = FBrefScraper()
        return scraper.scrape_team_stats(squad_id=str(team_id))

    def fetch_proxy_xg(team_id: int):
        # Fallback to calculation
        team_stats = {
            'shots_on_target': 50,
            'shots_off_target': 30,
            'big_chances_created': 10
        }
        return calculate_xg_proxy(team_stats)

    # Set up waterfall
    xg_fetcher = WaterfallFetcher([
        DataSource(
            name="understat",
            fetcher=fetch_from_understat,
            confidence=0.95,
            timeout=15
        ),
        DataSource(
            name="fbref",
            fetcher=fetch_from_fbref,
            confidence=0.85,
            timeout=10
        ),
        DataSource(
            name="proxy_calculation",
            fetcher=fetch_proxy_xg,
            confidence=0.60,
            timeout=1
        )
    ])

    return xg_fetcher
