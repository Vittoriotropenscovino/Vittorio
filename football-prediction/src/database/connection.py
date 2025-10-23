"""Database connection management"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .models import Base

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/football_predictions')


def get_engine(echo: bool = False) -> Engine:
    """
    Create and return SQLAlchemy engine

    Args:
        echo: If True, log all SQL statements

    Returns:
        SQLAlchemy Engine instance
    """
    engine = create_engine(
        DATABASE_URL,
        echo=echo,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
    )

    # Set up connection event listeners for PostgreSQL optimization
    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_conn, connection_record):
        """Set search path on connection"""
        cursor = dbapi_conn.cursor()
        cursor.execute("SET TIME ZONE 'UTC'")
        cursor.close()

    return engine


def get_sessionmaker(engine: Engine = None) -> sessionmaker:
    """
    Create and return session factory

    Args:
        engine: SQLAlchemy engine (creates new one if not provided)

    Returns:
        SQLAlchemy sessionmaker
    """
    if engine is None:
        engine = get_engine()

    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def get_session() -> Session:
    """
    Get a new database session

    Returns:
        SQLAlchemy Session instance
    """
    SessionLocal = get_sessionmaker()
    return SessionLocal()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions

    Usage:
        with get_db() as db:
            user = db.query(User).first()

    Yields:
        SQLAlchemy Session instance
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine: Engine = None, drop_all: bool = False):
    """
    Initialize database tables

    Args:
        engine: SQLAlchemy engine (creates new one if not provided)
        drop_all: If True, drop all existing tables before creating
    """
    if engine is None:
        engine = get_engine()

    if drop_all:
        print("WARNING: Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete!")


def test_connection() -> bool:
    """
    Test database connection

    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            return result.fetchone()[0] == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connection when run directly
    print("Testing database connection...")
    if test_connection():
        print("✓ Database connection successful!")

        # Initialize tables
        response = input("Initialize database tables? (y/n): ")
        if response.lower() == 'y':
            drop = input("Drop existing tables first? (y/n): ")
            init_db(drop_all=(drop.lower() == 'y'))
    else:
        print("✗ Database connection failed!")
