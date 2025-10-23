"""Data collection orchestrator - coordinates all data sources"""

import logging
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime

import numpy as np

from .api_clients import APIFootballClient, OpenWeatherClient
from .scrapers import UnderstatScraper, FBrefScraper, TransfermarktScraper
from .fallback import (
    WaterfallFetcher,
    DataSource,
    calculate_xg_proxy,
    calculate_importance_proxy,
    calculate_form_proxy,
)

logger = logging.getLogger(__name__)


@dataclass
class MatchAnalysisInput:
    """Input data for match analysis"""
    match_id: int
    home_team_id: int
    away_team_id: int
    match_datetime: str
    competition_id: int


class DataCollectionOrchestrator:
    """
    Orchestrates data collection from all sources

    Coordinates parallel fetching from:
    - API sources (API-Football, etc.)
    - Web scraping (Understat, FBref, etc.)
    - Database historical data
    - Fallback calculations
    """

    def __init__(self, match_input: MatchAnalysisInput):
        """
        Initialize orchestrator

        Args:
            match_input: Match details for analysis
        """
        self.match = match_input
        self.data = {}
        self.errors = []
        self.confidence_scores = {}

        # Initialize clients
        self.api_client = APIFootballClient()
        self.weather_client = OpenWeatherClient()

    async def collect_all_data(self) -> Dict:
        """
        Collect all data in parallel

        Returns:
            Dict containing all collected data with metadata
        """
        logger.info(f"Starting data collection for match {self.match.match_id}")

        # Define all async tasks
        tasks = {
            "fixture_data": self.fetch_fixture_details(),
            "team_stats_home": self.fetch_team_stats(self.match.home_team_id),
            "team_stats_away": self.fetch_team_stats(self.match.away_team_id),
            "h2h": self.fetch_head_to_head(),
            "injuries_home": self.fetch_injuries(self.match.home_team_id),
            "injuries_away": self.fetch_injuries(self.match.away_team_id),
            "weather": self.fetch_weather_data(),
            "odds": self.fetch_betting_odds(),
            "standings": self.fetch_standings(),
        }

        # Execute all tasks in parallel
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )

        # Map results
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {key}: {result}")
                self.errors.append({key: str(result)})
                self.data[key] = None
            else:
                self.data[key] = result.get('data')
                self.confidence_scores[key] = result.get('confidence', 0.5)

        # Calculate overall confidence
        self.data['_meta'] = {
            'overall_confidence': self._calculate_overall_confidence(),
            'missing_data': [k for k, v in self.data.items() if v is None and k != '_meta'],
            'errors': self.errors,
            'collection_timestamp': datetime.now().isoformat()
        }

        logger.info(
            f"Data collection complete. Confidence: {self.data['_meta']['overall_confidence']:.1%}"
        )

        # Close async sessions
        await self.api_client.close()
        await self.weather_client.close()

        return self.data

    def _calculate_overall_confidence(self) -> float:
        """Calculate weighted confidence score"""
        weights = {
            'fixture_data': 0.20,
            'team_stats_home': 0.15,
            'team_stats_away': 0.15,
            'h2h': 0.10,
            'injuries_home': 0.10,
            'injuries_away': 0.10,
            'odds': 0.10,
            'standings': 0.05,
            'weather': 0.05
        }

        weighted_sum = sum(
            self.confidence_scores.get(key, 0) * weight
            for key, weight in weights.items()
        )

        return round(weighted_sum, 3)

    async def fetch_fixture_details(self) -> Dict:
        """Fetch fixture details from API-Football"""
        try:
            logger.info("Fetching fixture details...")
            data = await self.api_client.get_fixture_async(self.match.match_id)

            return {
                "data": data['response'][0] if data.get('response') else None,
                "confidence": 0.95,
                "source": "api-football"
            }

        except Exception as e:
            logger.error(f"Fixture fetch failed: {e}")
            raise

    async def fetch_team_stats(self, team_id: int) -> Dict:
        """
        Fetch team statistics with fallback

        Tries:
        1. API-Football (recent matches)
        2. xG data from Understat
        3. Fallback calculations
        """
        try:
            logger.info(f"Fetching team stats for team {team_id}...")

            # Get recent fixtures from API
            fixtures_data = await self.api_client.get_async(
                "/fixtures",
                {"team": team_id, "last": 10}
            )

            # Calculate aggregate stats
            stats = self._aggregate_team_stats(
                fixtures_data.get('response', []),
                team_id
            )

            # Try to enhance with xG data
            try:
                xg_data = await self._fetch_xg_data(team_id)
                stats.update(xg_data)
            except Exception as e:
                logger.warning(f"xG fetch failed, using proxy: {e}")
                stats['xG'] = calculate_xg_proxy(stats)
                stats['xG_source'] = 'proxy'

            return {
                "data": stats,
                "confidence": 0.85,
                "source": "mixed"
            }

        except Exception as e:
            logger.error(f"Team stats fetch failed: {e}")
            # Return minimal fallback data
            return {
                "data": self._get_fallback_team_stats(team_id),
                "confidence": 0.50,
                "source": "fallback"
            }

    def _aggregate_team_stats(self, fixtures: List[Dict], team_id: int) -> Dict:
        """Calculate aggregate statistics from recent fixtures"""
        if not fixtures:
            return {}

        goals_scored = []
        goals_conceded = []
        possession = []
        shots = []
        shots_on_target = []

        for fixture in fixtures:
            # Determine team side
            is_home = fixture['teams']['home']['id'] == team_id
            team_side = 'home' if is_home else 'away'
            opp_side = 'away' if is_home else 'home'

            # Goals
            if fixture['goals'][team_side] is not None:
                goals_scored.append(fixture['goals'][team_side])
            if fixture['goals'][opp_side] is not None:
                goals_conceded.append(fixture['goals'][opp_side])

            # Statistics (if available)
            if 'statistics' in fixture:
                for stat_group in fixture.get('statistics', []):
                    if stat_group['team']['id'] == team_id:
                        for stat in stat_group.get('statistics', []):
                            if stat['type'] == 'Ball Possession':
                                poss = stat['value']
                                if poss and '%' in str(poss):
                                    possession.append(int(poss.replace('%', '')))
                            elif stat['type'] == 'Total Shots':
                                if stat['value']:
                                    shots.append(int(stat['value']))
                            elif stat['type'] == 'Shots on Goal':
                                if stat['value']:
                                    shots_on_target.append(int(stat['value']))

        return {
            "avg_goals_scored": round(np.mean(goals_scored), 2) if goals_scored else 1.5,
            "avg_goals_conceded": round(np.mean(goals_conceded), 2) if goals_conceded else 1.2,
            "avg_possession": round(np.mean(possession), 1) if possession else 50.0,
            "avg_shots": round(np.mean(shots), 1) if shots else 12.0,
            "avg_shots_on_target": round(np.mean(shots_on_target), 1) if shots_on_target else 4.0,
            "form": self._calculate_form(fixtures, team_id),
            "matches_analyzed": len(fixtures)
        }

    def _calculate_form(self, fixtures: List[Dict], team_id: int) -> float:
        """Calculate form score from recent results"""
        results = []

        for fixture in fixtures[-5:]:  # Last 5 matches
            if fixture['fixture']['status']['short'] != 'FT':
                continue

            is_home = fixture['teams']['home']['id'] == team_id
            team_goals = fixture['goals']['home' if is_home else 'away']
            opp_goals = fixture['goals']['away' if is_home else 'home']

            if team_goals > opp_goals:
                results.append('W')
            elif team_goals == opp_goals:
                results.append('D')
            else:
                results.append('L')

        return calculate_form_proxy(results)

    async def _fetch_xg_data(self, team_id: int) -> Dict:
        """Fetch xG data from Understat"""
        # This would need team name mapping
        # For now, return empty dict
        return {}

    def _get_fallback_team_stats(self, team_id: int) -> Dict:
        """Fallback team statistics"""
        return {
            "avg_goals_scored": 1.5,
            "avg_goals_conceded": 1.2,
            "avg_possession": 50.0,
            "form": 5.0,
            "source": "fallback"
        }

    async def fetch_head_to_head(self) -> Dict:
        """Fetch head-to-head history"""
        try:
            logger.info("Fetching head-to-head data...")

            data = await self.api_client.get_async(
                "/fixtures/headtohead",
                {
                    "h2h": f"{self.match.home_team_id}-{self.match.away_team_id}",
                    "last": 10
                }
            )

            return {
                "data": self._process_h2h(data.get('response', [])),
                "confidence": 0.90,
                "source": "api-football"
            }

        except Exception as e:
            logger.error(f"H2H fetch failed: {e}")
            return {"data": None, "confidence": 0, "source": "none"}

    def _process_h2h(self, fixtures: List[Dict]) -> Optional[Dict]:
        """Process head-to-head fixtures"""
        if not fixtures:
            return None

        home_wins = 0
        away_wins = 0
        draws = 0
        home_goals = []
        away_goals = []

        for fixture in fixtures:
            h_score = fixture['goals']['home']
            a_score = fixture['goals']['away']

            if h_score is None or a_score is None:
                continue

            home_goals.append(h_score)
            away_goals.append(a_score)

            if h_score > a_score:
                home_wins += 1
            elif a_score > h_score:
                away_wins += 1
            else:
                draws += 1

        total = len([f for f in fixtures if f['goals']['home'] is not None])

        if total == 0:
            return None

        return {
            "matches_played": total,
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "home_win_pct": home_wins / total,
            "avg_home_goals": round(np.mean(home_goals), 2) if home_goals else 1.5,
            "avg_away_goals": round(np.mean(away_goals), 2) if away_goals else 1.2
        }

    async def fetch_injuries(self, team_id: int) -> Dict:
        """Fetch injury/suspension data"""
        try:
            logger.info(f"Fetching injuries for team {team_id}...")

            # Try API-Football first
            data = await self.api_client.get_async(
                "/injuries",
                {"team": team_id}
            )

            injuries = []
            for inj in data.get('response', []):
                player_data = inj.get('player', {})
                injury_data = inj.get('player', {})

                # Calculate importance (would need more player data)
                importance = 5.0  # Default importance

                injuries.append({
                    "player_id": player_data.get('id'),
                    "player_name": player_data.get('name'),
                    "type": injury_data.get('type', 'Unknown'),
                    "expected_return": injury_data.get('date'),
                    "importance": importance
                })

            return {
                "data": injuries,
                "confidence": 0.80,
                "source": "api-football"
            }

        except Exception as e:
            logger.warning(f"Injuries fetch failed: {e}")
            return {"data": [], "confidence": 0.50, "source": "fallback"}

    async def fetch_weather_data(self) -> Dict:
        """Fetch weather forecast for match"""
        try:
            logger.info("Fetching weather data...")

            # Would need stadium coordinates from database
            # For now, return None
            return {
                "data": None,
                "confidence": 0,
                "source": "none"
            }

        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {"data": None, "confidence": 0, "source": "none"}

    async def fetch_betting_odds(self) -> Dict:
        """Fetch betting odds"""
        try:
            logger.info("Fetching betting odds...")

            data = await self.api_client.get_odds_async(self.match.match_id)

            if not data.get('response'):
                return {"data": None, "confidence": 0, "source": "none"}

            # Extract odds from first bookmaker
            bookmakers = data['response'][0].get('bookmakers', [])
            if not bookmakers:
                return {"data": None, "confidence": 0, "source": "none"}

            bet365 = bookmakers[0]
            market_1x2 = next(
                (m for m in bet365.get('bets', []) if m['name'] == 'Match Winner'),
                None
            )

            if not market_1x2:
                return {"data": None, "confidence": 0, "source": "none"}

            odds = {v['value']: float(v['odd']) for v in market_1x2['values']}

            return {
                "data": {
                    "odds_1": odds.get('Home', 2.0),
                    "odds_X": odds.get('Draw', 3.0),
                    "odds_2": odds.get('Away', 3.5),
                    "implied_prob_1": 1 / odds.get('Home', 2.0),
                    "implied_prob_X": 1 / odds.get('Draw', 3.0),
                    "implied_prob_2": 1 / odds.get('Away', 3.5),
                    "bookmaker": bet365.get('name', 'Unknown')
                },
                "confidence": 0.95,
                "source": "api-football-odds"
            }

        except Exception as e:
            logger.warning(f"Odds fetch failed: {e}")
            return {"data": None, "confidence": 0, "source": "none"}

    async def fetch_standings(self) -> Dict:
        """Fetch league standings"""
        try:
            logger.info("Fetching league standings...")

            # Get current season year
            current_year = datetime.now().year

            data = await self.api_client.get_async(
                "/standings",
                {"league": self.match.competition_id, "season": current_year}
            )

            if not data.get('response'):
                return {"data": None, "confidence": 0.50, "source": "none"}

            standings = data['response'][0]['league']['standings'][0]

            home_team = next(
                (t for t in standings if t['team']['id'] == self.match.home_team_id),
                None
            )
            away_team = next(
                (t for t in standings if t['team']['id'] == self.match.away_team_id),
                None
            )

            if not home_team or not away_team:
                return {"data": None, "confidence": 0.50, "source": "partial"}

            return {
                "data": {
                    "home_position": home_team['rank'],
                    "away_position": away_team['rank'],
                    "home_points": home_team['points'],
                    "away_points": away_team['points'],
                    "home_form_str": home_team.get('form', 'DDDDD'),
                    "away_form_str": away_team.get('form', 'DDDDD')
                },
                "confidence": 0.95,
                "source": "api-football"
            }

        except Exception as e:
            logger.warning(f"Standings fetch failed: {e}")
            return {"data": None, "confidence": 0.50, "source": "none"}
