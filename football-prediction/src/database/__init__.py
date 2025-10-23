"""Database module for Football Prediction System"""

from .models import (
    Base,
    Competition,
    Team,
    Stadium,
    TeamRivalry,
    Match,
    TeamStats,
    PlayerAvailability,
    Prediction,
    PredictionResult,
)
from .connection import (
    get_engine,
    get_session,
    init_db,
    get_db,
)

__all__ = [
    # Models
    'Base',
    'Competition',
    'Team',
    'Stadium',
    'TeamRivalry',
    'Match',
    'TeamStats',
    'PlayerAvailability',
    'Prediction',
    'PredictionResult',
    # Connection
    'get_engine',
    'get_session',
    'init_db',
    'get_db',
]
