"""SQLAlchemy database models for Football Prediction System"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Text, Boolean,
    ForeignKey, CheckConstraint, UniqueConstraint, Index, BigInteger
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Competition(Base):
    """Football competitions/leagues"""
    __tablename__ = 'competitions'

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    matches = relationship("Match", back_populates="competition")


class Team(Base):
    """Football teams"""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    short_name = Column(String(50))
    country = Column(String(50))
    founded = Column(Integer)
    logo_url = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    stats = relationship("TeamStats", back_populates="team")
    stadium = relationship("Stadium", back_populates="team", uselist=False)
    player_availability = relationship("PlayerAvailability", back_populates="team")


class Stadium(Base):
    """Team stadiums with geolocation"""
    __tablename__ = 'stadiums'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), unique=True)
    name = Column(String(100))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    capacity = Column(Integer)
    avg_attendance_pct = Column(Numeric(4, 3))
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    team = relationship("Team", back_populates="stadium")


class TeamRivalry(Base):
    """Pre-defined team rivalries"""
    __tablename__ = 'team_rivalries'

    id = Column(Integer, primary_key=True)
    team_a_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    team_b_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    rivalry_level = Column(Integer, CheckConstraint('rivalry_level BETWEEN 1 AND 10'))
    rivalry_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('team_a_id', 'team_b_id', name='unique_rivalry'),
    )


class Match(Base):
    """Football matches"""
    __tablename__ = 'matches'

    match_id = Column(BigInteger, primary_key=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    match_datetime = Column(DateTime(timezone=True))
    status = Column(String(20))
    home_score = Column(Integer)
    away_score = Column(Integer)
    venue = Column(String(100))
    referee = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    competition = relationship("Competition", back_populates="matches")
    stats = relationship("TeamStats", back_populates="match")
    predictions = relationship("Prediction", back_populates="match")
    player_availability = relationship("PlayerAvailability", back_populates="match")

    # Indexes
    __table_args__ = (
        Index('idx_matches_datetime', 'match_datetime'),
        Index('idx_matches_status', 'status'),
        Index('idx_matches_competition', 'competition_id'),
        Index('idx_matches_teams', 'home_team_id', 'away_team_id'),
    )


class TeamStats(Base):
    """Team statistics per match"""
    __tablename__ = 'team_stats'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    match_id = Column(BigInteger, ForeignKey('matches.match_id'))
    season = Column(String(10))

    # Goals
    xg = Column(Numeric(4, 2))
    xga = Column(Numeric(4, 2))
    goals_scored = Column(Integer)
    goals_conceded = Column(Integer)

    # Possession & Passing
    possession = Column(Numeric(4, 1))
    passes_completed = Column(Integer)
    passes_attempted = Column(Integer)
    pass_accuracy = Column(Numeric(4, 1))

    # Shots
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    shots_off_target = Column(Integer)

    # Defensive
    tackles = Column(Integer)
    interceptions = Column(Integer)
    ppda = Column(Numeric(5, 2))

    # Metadata
    data_source = Column(String(50))
    confidence = Column(Numeric(3, 2))
    fetched_at = Column(DateTime, default=datetime.now)

    # Relationships
    team = relationship("Team", back_populates="stats")
    match = relationship("Match", back_populates="stats")

    __table_args__ = (
        UniqueConstraint('team_id', 'match_id', name='unique_team_match_stats'),
        Index('idx_team_stats_team', 'team_id'),
        Index('idx_team_stats_match', 'match_id'),
        Index('idx_team_stats_season', 'season'),
    )


class PlayerAvailability(Base):
    """Player injuries and suspensions"""
    __tablename__ = 'player_availability'

    id = Column(Integer, primary_key=True)
    player_id = Column(BigInteger, nullable=False)
    player_name = Column(String(100))
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    match_id = Column(BigInteger, ForeignKey('matches.match_id'))
    status = Column(String(20))
    injury_type = Column(String(100))
    importance_score = Column(Numeric(3, 1), CheckConstraint('importance_score BETWEEN 1.0 AND 10.0'))
    expected_return = Column(DateTime)
    data_source = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    team = relationship("Team", back_populates="player_availability")
    match = relationship("Match", back_populates="player_availability")

    __table_args__ = (
        Index('idx_player_availability_team', 'team_id'),
        Index('idx_player_availability_match', 'match_id'),
        Index('idx_player_availability_status', 'status'),
    )


class Prediction(Base):
    """Match predictions"""
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    match_id = Column(BigInteger, ForeignKey('matches.match_id'), nullable=False)

    # Probabilities
    prob_home = Column(Numeric(4, 3), CheckConstraint('prob_home BETWEEN 0 AND 1'))
    prob_draw = Column(Numeric(4, 3), CheckConstraint('prob_draw BETWEEN 0 AND 1'))
    prob_away = Column(Numeric(4, 3), CheckConstraint('prob_away BETWEEN 0 AND 1'))

    # Expected goals
    predicted_score_home = Column(Numeric(3, 1))
    predicted_score_away = Column(Numeric(3, 1))

    # Most likely
    most_likely_result = Column(String(1))
    most_likely_score = Column(String(10))

    # Quality metrics
    confidence = Column(Numeric(3, 2))
    data_quality = Column(String(10))

    # Model info
    model_version = Column(String(20))
    ensemble_method = Column(String(50))

    # Raw data
    raw_features = Column(JSONB)
    warnings = Column(JSONB)

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    match = relationship("Match", back_populates="predictions")
    result = relationship("PredictionResult", back_populates="prediction", uselist=False)

    __table_args__ = (
        CheckConstraint(
            'ABS((prob_home + prob_draw + prob_away) - 1.0) < 0.01',
            name='prob_sum_check'
        ),
        Index('idx_predictions_match', 'match_id'),
        Index('idx_predictions_created', 'created_at'),
    )


class PredictionResult(Base):
    """Post-match prediction evaluation"""
    __tablename__ = 'prediction_results'

    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Actual outcome
    actual_result = Column(String(1))
    actual_score = Column(String(10))

    # Evaluation
    predicted_result = Column(String(1))
    correct_result = Column(Boolean)
    probability_actual = Column(Numeric(4, 3))

    # Accuracy metrics
    brier_score = Column(Numeric(5, 4))
    log_loss = Column(Numeric(6, 4))

    # Analysis
    factors_review = Column(JSONB)

    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    prediction = relationship("Prediction", back_populates="result")

    __table_args__ = (
        Index('idx_prediction_results_prediction', 'prediction_id'),
        Index('idx_prediction_results_correct', 'correct_result'),
    )
