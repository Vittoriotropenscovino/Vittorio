"""Database setup script"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def setup_database():
    """Setup database schema and initial data"""

    print("\n" + "="*60)
    print("FOOTBALL PREDICTION SYSTEM - Database Setup")
    print("="*60 + "\n")

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Test connection
    print("1. Testing database connection...")
    from database.connection import test_connection

    if not test_connection():
        print("❌ Database connection failed!")
        print("\nPlease check:")
        print("  - PostgreSQL is running")
        print("  - DATABASE_URL in .env is correct")
        print("  - Database exists: createdb football_predictions")
        sys.exit(1)

    print("✅ Database connection successful!\n")

    # Initialize schema
    print("2. Initializing database schema...")

    response = input("This will create all tables. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    drop_existing = input("Drop existing tables first? (y/n): ")

    from database.connection import init_db

    try:
        init_db(drop_all=(drop_existing.lower() == 'y'))
        print("✅ Database schema initialized!\n")
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        sys.exit(1)

    # Optional: Load seed data
    print("3. Load seed data (optional)...")

    response = input("Load example teams and competitions? (y/n): ")
    if response.lower() == 'y':
        try:
            load_seed_data()
            print("✅ Seed data loaded!\n")
        except Exception as e:
            print(f"⚠️  Seed data failed (non-critical): {e}\n")

    print("="*60)
    print("✅ Database setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Configure API keys in .env")
    print("  2. Run a test prediction: python src/pipeline.py <match_id>")
    print("  3. Start scheduler: python src/scheduler.py")
    print()


def load_seed_data():
    """Load example seed data"""
    from database import get_db
    from database.models import Competition, Team, Stadium

    with get_db() as db:
        # Competitions
        competitions = [
            Competition(external_id=39, name="Premier League", country="England", type="League"),
            Competition(external_id=140, name="La Liga", country="Spain", type="League"),
            Competition(external_id=135, name="Serie A", country="Italy", type="League"),
            Competition(external_id=78, name="Bundesliga", country="Germany", type="League"),
        ]

        for comp in competitions:
            existing = db.query(Competition).filter_by(external_id=comp.external_id).first()
            if not existing:
                db.add(comp)

        # Stadiums (examples)
        stadiums = [
            Stadium(
                name="Camp Nou",
                city="Barcelona",
                country="Spain",
                capacity=99354,
                latitude=41.380896,
                longitude=2.122820,
                surface="grass"
            ),
            Stadium(
                name="Old Trafford",
                city="Manchester",
                country="England",
                capacity=74879,
                latitude=53.463056,
                longitude=-2.291389,
                surface="grass"
            ),
        ]

        for stadium in stadiums:
            existing = db.query(Stadium).filter_by(name=stadium.name).first()
            if not existing:
                db.add(stadium)

        db.commit()

        print(f"  Loaded {len(competitions)} competitions")
        print(f"  Loaded {len(stadiums)} stadiums")


if __name__ == "__main__":
    setup_database()
