"""Data collection module for Football Prediction System"""

from .api_clients import (
    FootballDataClient,
    APIFootballClient,
    OpenWeatherClient,
)
from .scrapers import (
    UnderstatScraper,
    FBrefScraper,
    TransfermarktScraper,
)
from .fallback import (
    WaterfallFetcher,
    DataSource,
    calculate_xg_proxy,
    calculate_importance_proxy,
)
from .orchestrator import (
    MatchAnalysisInput,
    DataCollectionOrchestrator,
)

__all__ = [
    # API Clients
    'FootballDataClient',
    'APIFootballClient',
    'OpenWeatherClient',
    # Scrapers
    'UnderstatScraper',
    'FBrefScraper',
    'TransfermarktScraper',
    # Fallback
    'WaterfallFetcher',
    'DataSource',
    'calculate_xg_proxy',
    'calculate_importance_proxy',
    # Orchestrator
    'MatchAnalysisInput',
    'DataCollectionOrchestrator',
]
