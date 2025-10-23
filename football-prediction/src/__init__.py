"""Football Prediction System - Main Package"""

__version__ = "3.0.0"
__author__ = "AI Football Prediction System"

# Make key modules easily accessible
from . import data_collection
from . import processing
from . import models
from . import validation
from . import output
from . import learning
from . import database

__all__ = [
    'data_collection',
    'processing',
    'models',
    'validation',
    'output',
    'learning',
    'database',
]
