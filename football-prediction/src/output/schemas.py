"""Pydantic schemas for prediction output"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict


class PredictionOutput(BaseModel):
    """Structured prediction output"""

    # Metadata
    match_id: int
    home_team: str
    away_team: str
    competition: str
    match_datetime: datetime
    generated_at: datetime = Field(default_factory=datetime.now)
    model_version: str = "3.0-auto"

    # Main predictions
    probabilities: Dict[str, float] = Field(
        ...,
        example={"1": 0.450, "X": 0.300, "2": 0.250}
    )
    most_likely_result: str = Field(..., example="1")
    most_likely_score: str = Field(..., example="2-1")

    # Expected metrics
    expected_goals: Dict[str, float] = Field(
        ...,
        example={"home": 1.8, "away": 1.2}
    )

    # Supplementary markets
    over_under_2_5: Dict[str, float]
    both_teams_score: Dict[str, float]
    clean_sheet_probability: Dict[str, float]
    top_correct_scores: List[Dict[str, any]]

    # Confidence & Quality
    confidence: float = Field(..., ge=0, le=1)
    data_quality: str = Field(..., example="HIGH")

    # Value betting
    value_bets: List[Dict[str, any]] = []

    # Analysis factors
    key_factors: Dict[str, List[str]] = Field(
        ...,
        example={
            "pro_home": ["Superior form", "Home advantage"],
            "pro_away": ["Strong away record"],
            "neutral": ["Even H2H record"]
        }
    )

    # Warnings & Notes
    warnings: List[str] = []
    data_sources_used: List[str] = []
    missing_data: List[str] = []

    # Raw features (optional, for debugging)
    raw_features: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "match_id": 1035480,
                "home_team": "FC Barcelona",
                "away_team": "Real Madrid",
                "competition": "La Liga",
                "match_datetime": "2025-01-15T21:00:00",
                "probabilities": {"1": 0.45, "X": 0.30, "2": 0.25},
                "most_likely_result": "1",
                "most_likely_score": "2-1",
                "confidence": 0.85,
                "data_quality": "HIGH"
            }
        }
