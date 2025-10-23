"""API clients for external football data sources"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

import requests
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Base class for API clients"""

    def __init__(self, api_key: str = None, timeout: int = 10):
        self.api_key = api_key or self._get_api_key()
        self.timeout = timeout
        self.session = None

    @abstractmethod
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """Get base URL for API"""
        pass

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make GET request with retry logic

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON
        """
        url = f"{self._get_base_url()}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {url} - {e}")
            raise

    async def get_async(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Async GET request

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON
        """
        url = f"{self._get_base_url()}{endpoint}"
        headers = self._get_headers()

        if self.session is None:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Async API request failed: {url} - {e}")
            raise

    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()


class FootballDataClient(BaseAPIClient):
    """Client for Football-Data.org API"""

    def _get_api_key(self) -> str:
        return os.getenv('FOOTBALL_DATA_API_KEY', '')

    def _get_base_url(self) -> str:
        return "https://api.football-data.org/v4"

    def _get_headers(self) -> Dict[str, str]:
        return {"X-Auth-Token": self.api_key}

    def get_match_details(self, match_id: int) -> Dict:
        """Get match details"""
        return self.get(f"/matches/{match_id}")

    def get_team_matches(self, team_id: int, limit: int = 10) -> Dict:
        """Get team's recent matches"""
        return self.get(f"/teams/{team_id}/matches", {"limit": limit})

    def get_head_to_head(self, match_id: int, limit: int = 10) -> Dict:
        """Get head-to-head matches"""
        return self.get(f"/matches/{match_id}/head2head", {"limit": limit})

    def get_standings(self, competition_id: int, season: int = None) -> Dict:
        """Get competition standings"""
        params = {}
        if season:
            params['season'] = season
        return self.get(f"/competitions/{competition_id}/standings", params)

    async def get_match_details_async(self, match_id: int) -> Dict:
        """Async: Get match details"""
        return await self.get_async(f"/matches/{match_id}")


class APIFootballClient(BaseAPIClient):
    """Client for API-Football (RapidAPI)"""

    def _get_api_key(self) -> str:
        return os.getenv('RAPIDAPI_KEY', '')

    def _get_base_url(self) -> str:
        return "https://v3.football.api-sports.io"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

    def get_fixture(self, fixture_id: int) -> Dict:
        """Get fixture details"""
        return self.get("/fixtures", {"id": fixture_id})

    def get_fixture_statistics(self, fixture_id: int) -> Dict:
        """Get fixture statistics"""
        return self.get("/fixtures/statistics", {"fixture": fixture_id})

    def get_fixture_lineups(self, fixture_id: int) -> Dict:
        """Get fixture lineups"""
        return self.get("/fixtures/lineups", {"fixture": fixture_id})

    def get_fixture_players(self, fixture_id: int) -> Dict:
        """Get fixture player statistics"""
        return self.get("/fixtures/players", {"fixture": fixture_id})

    def get_team_fixtures(self, team_id: int, last: int = 10, season: int = None) -> Dict:
        """Get team fixtures"""
        params = {"team": team_id, "last": last}
        if season:
            params['season'] = season
        return self.get("/fixtures", params)

    def get_injuries(self, team_id: int, season: int = None) -> Dict:
        """Get team injuries"""
        params = {"team": team_id}
        if season:
            params['season'] = season
        return self.get("/injuries", params)

    def get_odds(self, fixture_id: int) -> Dict:
        """Get betting odds for fixture"""
        return self.get("/odds", {"fixture": fixture_id})

    def get_standings(self, league_id: int, season: int) -> Dict:
        """Get league standings"""
        return self.get("/standings", {"league": league_id, "season": season})

    def get_h2h(self, team1_id: int, team2_id: int, last: int = 10) -> Dict:
        """Get head-to-head matches"""
        return self.get("/fixtures/headtohead", {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last
        })

    async def get_fixture_async(self, fixture_id: int) -> Dict:
        """Async: Get fixture details"""
        return await self.get_async("/fixtures", {"id": fixture_id})

    async def get_fixture_statistics_async(self, fixture_id: int) -> Dict:
        """Async: Get fixture statistics"""
        return await self.get_async("/fixtures/statistics", {"fixture": fixture_id})

    async def get_fixture_lineups_async(self, fixture_id: int) -> Dict:
        """Async: Get fixture lineups"""
        return await self.get_async("/fixtures/lineups", {"fixture": fixture_id})

    async def get_odds_async(self, fixture_id: int) -> Dict:
        """Async: Get betting odds"""
        return await self.get_async("/odds", {"fixture": fixture_id})


class OpenWeatherClient(BaseAPIClient):
    """Client for OpenWeatherMap API"""

    def _get_api_key(self) -> str:
        return os.getenv('OPENWEATHER_API_KEY', '')

    def _get_base_url(self) -> str:
        return "https://api.openweathermap.org/data/2.5"

    def get_forecast(self, lat: float, lon: float) -> Dict:
        """Get weather forecast for coordinates"""
        return self.get("/forecast", {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        })

    def get_match_weather(
        self,
        stadium_coords: tuple,
        match_datetime: str
    ) -> Optional[Dict]:
        """
        Get weather forecast for match time

        Args:
            stadium_coords: (latitude, longitude)
            match_datetime: ISO format datetime string

        Returns:
            Weather forecast dict or None
        """
        try:
            lat, lon = stadium_coords
            forecasts = self.get_forecast(lat, lon)

            match_time = datetime.fromisoformat(match_datetime.replace('Z', '+00:00'))

            # Find closest forecast to match time
            closest = None
            min_diff = float('inf')

            for forecast in forecasts.get('list', []):
                forecast_time = datetime.fromtimestamp(forecast['dt'])
                diff = abs((forecast_time - match_time).total_seconds())

                if diff < min_diff:
                    min_diff = diff
                    closest = forecast

            if closest:
                return {
                    "temperature": closest['main']['temp'],
                    "feels_like": closest['main']['feels_like'],
                    "humidity": closest['main']['humidity'],
                    "wind_speed": closest['wind']['speed'],
                    "wind_deg": closest['wind'].get('deg'),
                    "conditions": closest['weather'][0]['main'],
                    "description": closest['weather'][0]['description'],
                    "precipitation_prob": closest.get('pop', 0) * 100,
                    "clouds": closest.get('clouds', {}).get('all', 0),
                    "forecast_time": datetime.fromtimestamp(closest['dt']).isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return None

    async def get_forecast_async(self, lat: float, lon: float) -> Dict:
        """Async: Get weather forecast"""
        return await self.get_async("/forecast", {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        })


# Factory function
def get_api_client(client_type: str) -> BaseAPIClient:
    """
    Get API client by type

    Args:
        client_type: 'football-data', 'api-football', or 'weather'

    Returns:
        API client instance
    """
    clients = {
        'football-data': FootballDataClient,
        'api-football': APIFootballClient,
        'weather': OpenWeatherClient,
    }

    client_class = clients.get(client_type.lower())
    if not client_class:
        raise ValueError(f"Unknown client type: {client_type}")

    return client_class()
