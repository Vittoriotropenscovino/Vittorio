"""System test script - Validate complete installation"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("\n" + "="*60)
print("FOOTBALL PREDICTION SYSTEM - System Test")
print("="*60 + "\n")

# Load environment
from dotenv import load_dotenv
load_dotenv()

test_results = {
    "passed": [],
    "failed": []
}


def test_imports():
    """Test 1: All imports work"""
    print("Test 1: Checking imports...")

    try:
        # Core modules
        from data_collection import api_clients, scrapers, orchestrator
        from processing import processor
        from models import prediction_model, supplementary
        from validation import validator
        from output import schemas, report_generator
        from learning import post_match
        from database import models, connection

        # Main modules
        import pipeline
        import scheduler

        print("  ✅ All imports successful")
        test_results["passed"].append("Imports")
        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        test_results["failed"].append(f"Imports: {e}")
        return False


def test_database():
    """Test 2: Database connection"""
    print("\nTest 2: Database connection...")

    try:
        from database.connection import test_connection

        if test_connection():
            print("  ✅ Database connection successful")
            test_results["passed"].append("Database Connection")
            return True
        else:
            print("  ❌ Database connection failed")
            test_results["failed"].append("Database Connection: Failed to connect")
            return False

    except Exception as e:
        print(f"  ❌ Database test error: {e}")
        test_results["failed"].append(f"Database Connection: {e}")
        return False


def test_api_clients():
    """Test 3: API clients initialization"""
    print("\nTest 3: API clients...")

    try:
        from data_collection.api_clients import (
            FootballDataClient,
            APIFootballClient,
            OpenWeatherClient
        )

        # Initialize clients
        fd_client = FootballDataClient()
        api_client = APIFootballClient()
        weather_client = OpenWeatherClient()

        # Check API keys
        if not fd_client.api_key:
            print("  ⚠️  Warning: FOOTBALL_DATA_API_KEY not set")
        if not api_client.api_key:
            print("  ⚠️  Warning: RAPIDAPI_KEY not set")
        if not weather_client.api_key:
            print("  ⚠️  Warning: OPENWEATHER_API_KEY not set")

        print("  ✅ API clients initialized")
        test_results["passed"].append("API Clients")
        return True

    except Exception as e:
        print(f"  ❌ API client error: {e}")
        test_results["failed"].append(f"API Clients: {e}")
        return False


def test_data_processor():
    """Test 4: Data processor with mock data"""
    print("\nTest 4: Data processor...")

    try:
        from processing.processor import DataProcessor

        # Mock data
        mock_data = {
            'team_stats_home': {
                'data': {
                    'form': 7.0,
                    'avg_goals_scored': 2.1,
                    'avg_goals_conceded': 1.0,
                    'avg_possession': 58.0
                }
            },
            'team_stats_away': {
                'data': {
                    'form': 5.0,
                    'avg_goals_scored': 1.5,
                    'avg_goals_conceded': 1.3,
                    'avg_possession': 48.0
                }
            },
            'injuries_home': {'data': []},
            'injuries_away': {'data': []},
            'h2h': {'data': None},
            'weather': {'data': None},
            'standings': {'data': None},
            '_meta': {'overall_confidence': 0.75}
        }

        processor = DataProcessor(mock_data)
        features = processor.process()

        assert 'home_form' in features
        assert 'away_form' in features

        print(f"  ✅ Data processor working ({len(features)} features generated)")
        test_results["passed"].append("Data Processor")
        return True

    except Exception as e:
        print(f"  ❌ Data processor error: {e}")
        test_results["failed"].append(f"Data Processor: {e}")
        return False


def test_prediction_model():
    """Test 5: Prediction model with mock features"""
    print("\nTest 5: Prediction model...")

    try:
        from models.prediction_model import PredictionModel

        # Mock features
        features = {
            'home_form': 7.0,
            'away_form': 5.0,
            'home_squad_quality': 8.0,
            'away_squad_quality': 6.0,
            'home_motivation': 7.0,
            'away_motivation': 6.0,
            'home_physical_condition': 9.0,
            'away_physical_condition': 8.0,
            'home_field_advantage': 6.5,
            'home_avg_goals': 2.0,
            'away_avg_goals': 1.5,
            'home_avg_conceded': 1.0,
            'away_avg_conceded': 1.3,
            'tactical_matchup_score': 0.2,
            'h2h_home_advantage': 0.3,
            '_meta': {'overall_confidence': 0.75}
        }

        config = {
            'weights': {
                'form': 0.25,
                'squad_quality': 0.20,
                'motivation': 0.15,
                'physical_condition': 0.15,
                'home_advantage': 0.10,
                'tactical': 0.10,
                'psychological': 0.05
            }
        }

        model = PredictionModel(features, config)
        prediction = model.predict()

        assert 'probabilities' in prediction
        assert 'expected_goals' in prediction
        assert 'confidence' in prediction

        probs = prediction['probabilities']
        prob_sum = probs['1'] + probs['X'] + probs['2']

        assert abs(prob_sum - 1.0) < 0.01

        print(f"  ✅ Prediction model working")
        print(f"     Probabilities: 1={probs['1']:.1%} X={probs['X']:.1%} 2={probs['2']:.1%}")
        print(f"     Confidence: {prediction['confidence']:.1%}")
        test_results["passed"].append("Prediction Model")
        return True

    except Exception as e:
        print(f"  ❌ Prediction model error: {e}")
        test_results["failed"].append(f"Prediction Model: {e}")
        return False


def test_validation():
    """Test 6: Validation system"""
    print("\nTest 6: Validation system...")

    try:
        from validation.validator import PredictionValidator

        # Mock prediction
        prediction = {
            'probabilities': {'1': 0.45, 'X': 0.30, '2': 0.25},
            'expected_goals': {'home': 1.8, 'away': 1.2},
            'confidence': 0.75
        }

        features = {'_meta': {'overall_confidence': 0.75}}

        validator = PredictionValidator(prediction, features)
        validation = validator.validate()

        assert 'validation_passed' in validation
        assert 'warnings' in validation
        assert 'errors' in validation

        print(f"  ✅ Validation system working")
        print(f"     Passed: {validation['validation_passed']}")
        print(f"     Warnings: {len(validation['warnings'])}")
        test_results["passed"].append("Validation")
        return True

    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        test_results["failed"].append(f"Validation: {e}")
        return False


def test_output():
    """Test 7: Output generation"""
    print("\nTest 7: Output generation...")

    try:
        from output.schemas import PredictionOutput
        from datetime import datetime

        # Create mock output
        output = PredictionOutput(
            match_id=999999,
            home_team="Test Home",
            away_team="Test Away",
            competition="Test League",
            match_datetime=datetime.now(),
            probabilities={'1': 0.45, 'X': 0.30, '2': 0.25},
            most_likely_result='1',
            most_likely_score='2-1',
            expected_goals={'home': 1.8, 'away': 1.2},
            over_under_2_5={'over_2.5': 0.55, 'under_2.5': 0.45},
            both_teams_score={'btts_yes': 0.60, 'btts_no': 0.40},
            clean_sheet_probability={'home_clean_sheet': 0.30, 'away_clean_sheet': 0.16},
            top_correct_scores=[
                {'score': '2-1', 'probability': 0.12},
                {'score': '1-1', 'probability': 0.10}
            ],
            confidence=0.75,
            data_quality='HIGH',
            key_factors={'pro_home': [], 'pro_away': [], 'neutral': []}
        )

        # Test JSON serialization
        json_str = output.model_dump_json()
        assert len(json_str) > 0

        print("  ✅ Output generation working")
        test_results["passed"].append("Output Generation")
        return True

    except Exception as e:
        print(f"  ❌ Output generation error: {e}")
        test_results["failed"].append(f"Output Generation: {e}")
        return False


# Print summary
def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    print(f"\n✅ Passed: {len(test_results['passed'])}")
    for test in test_results['passed']:
        print(f"   - {test}")

    if test_results['failed']:
        print(f"\n❌ Failed: {len(test_results['failed'])}")
        for test in test_results['failed']:
            print(f"   - {test}")

    total = len(test_results['passed']) + len(test_results['failed'])
    success_rate = len(test_results['passed']) / total * 100 if total > 0 else 0

    print(f"\nSuccess Rate: {success_rate:.0f}%")

    if not test_results['failed']:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Configure API keys in .env")
        print("  2. Run: python src/pipeline.py <match_id>")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")

    print("="*60 + "\n")


def main():
    """Run all tests"""

    test_imports()
    test_database()
    test_api_clients()
    test_data_processor()
    test_prediction_model()
    test_validation()
    test_output()

    print_summary()

    # Exit with error code if tests failed
    if test_results['failed']:
        sys.exit(1)


if __name__ == "__main__":
    main()
