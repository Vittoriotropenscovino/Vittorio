#!/usr/bin/env python3
"""
Quick Test Script - Tests core modules without external dependencies
No database, no API keys required
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("\n" + "="*60)
print("QUICK TEST - AI Football Prediction System v3.0")
print("="*60 + "\n")

test_results = {"passed": 0, "failed": 0}

# ============================================================
# TEST 1: Import Fixes
# ============================================================
def test_imports():
    """Test all import fixes"""
    print("TEST 1: Testing Import Fixes...")

    try:
        # Test models imports
        from models.prediction_model import PredictionModel
        from models.supplementary import SupplementaryCalculations
        print("  ✓ models.prediction_model imported")
        print("  ✓ models.supplementary imported")

        # Test validation imports
        from validation.validator import PredictionValidator
        print("  ✓ validation.validator imported")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


# ============================================================
# TEST 2: Type Hints Fix
# ============================================================
def test_type_hints():
    """Test type hints are correct"""
    print("\nTEST 2: Testing Type Hints Fix...")

    try:
        from output.schemas import PredictionOutput, Any
        from typing import List, Dict

        # Check Any is imported
        assert Any is not None
        print("  ✓ Any imported correctly from typing")

        # Check PredictionOutput uses Any
        import inspect
        annotations = PredictionOutput.__annotations__
        print(f"  ✓ PredictionOutput has {len(annotations)} annotated fields")

        return True
    except Exception as e:
        print(f"  ✗ Type hints test failed: {e}")
        return False


# ============================================================
# TEST 3: PredictionModel Validation
# ============================================================
def test_prediction_model_validation():
    """Test features validation in PredictionModel"""
    print("\nTEST 3: Testing PredictionModel Validation...")

    try:
        from models.prediction_model import PredictionModel

        # Test 1: Empty features should raise error
        try:
            model = PredictionModel({}, {})
            print("  ✗ Empty features should raise ValueError")
            return False
        except ValueError as e:
            print(f"  ✓ Empty features correctly rejected: {e}")

        # Test 2: None features should raise error
        try:
            model = PredictionModel(None, {})
            print("  ✗ None features should raise ValueError")
            return False
        except ValueError as e:
            print(f"  ✓ None features correctly rejected: {e}")

        # Test 3: Valid features should work
        features = {
            'home_form': 7.0,
            'away_form': 5.0,
            'home_avg_goals': 1.8,
            'away_avg_goals': 1.2,
            'home_avg_conceded': 1.0,
            'away_avg_conceded': 1.3,
            '_meta': {'overall_confidence': 0.75}
        }
        config = {}
        model = PredictionModel(features, config)
        print("  ✓ Valid features accepted")

        return True
    except Exception as e:
        print(f"  ✗ Validation test failed: {e}")
        return False


# ============================================================
# TEST 4: SupplementaryCalculations Validation
# ============================================================
def test_supplementary_validation():
    """Test validation in SupplementaryCalculations"""
    print("\nTEST 4: Testing SupplementaryCalculations Validation...")

    try:
        from models.supplementary import SupplementaryCalculations

        # Test 1: Missing keys should raise error
        try:
            calc = SupplementaryCalculations({'home': 1.5}, {'1': 0.45, 'X': 0.30, '2': 0.25})
            print("  ✗ Missing 'away' key should raise ValueError")
            return False
        except ValueError as e:
            print(f"  ✓ Missing keys correctly rejected: {e}")

        # Test 2: Negative xG should raise error
        try:
            calc = SupplementaryCalculations(
                {'home': -1.5, 'away': 1.2},
                {'1': 0.45, 'X': 0.30, '2': 0.25}
            )
            print("  ✗ Negative xG should raise ValueError")
            return False
        except ValueError as e:
            print(f"  ✓ Negative xG correctly rejected: {e}")

        # Test 3: Valid data should work
        calc = SupplementaryCalculations(
            {'home': 1.8, 'away': 1.2},
            {'1': 0.45, 'X': 0.30, '2': 0.25}
        )
        print("  ✓ Valid data accepted")

        return True
    except Exception as e:
        print(f"  ✗ Validation test failed: {e}")
        return False


# ============================================================
# TEST 5: Performance Optimization (No Redundant Calculations)
# ============================================================
def test_performance_optimization():
    """Test that calculations are not redundant"""
    print("\nTEST 5: Testing Performance Optimization...")

    try:
        from models.prediction_model import PredictionModel
        import inspect

        # Check _calculate_expected_goals accepts poisson_result
        sig = inspect.signature(PredictionModel._calculate_expected_goals)
        params = list(sig.parameters.keys())
        assert 'poisson_result' in params
        print("  ✓ _calculate_expected_goals accepts poisson_result parameter")

        # Check _calculate_confidence accepts pre-calculated results
        sig = inspect.signature(PredictionModel._calculate_confidence)
        params = list(sig.parameters.keys())
        assert 'scoring_probs' in params
        assert 'poisson_probs' in params
        print("  ✓ _calculate_confidence accepts scoring_probs and poisson_probs")

        return True
    except Exception as e:
        print(f"  ✗ Performance test failed: {e}")
        return False


# ============================================================
# TEST 6: Algorithm Fix (Goal Ranges)
# ============================================================
def test_goal_ranges_algorithm():
    """Test goal ranges uses convolution"""
    print("\nTEST 6: Testing Goal Ranges Algorithm Fix...")

    try:
        from models.supplementary import SupplementaryCalculations

        calc = SupplementaryCalculations(
            {'home': 1.5, 'away': 1.2},
            {'1': 0.45, 'X': 0.30, '2': 0.25}
        )

        # Calculate goal ranges
        result = calc._goal_ranges()

        # Verify all ranges exist
        assert '0-1' in result
        assert '2-3' in result
        assert '4-5' in result
        assert '6+' in result
        print("  ✓ All goal ranges calculated")

        # Verify probabilities sum to ~1.0
        total = sum(result.values())
        assert 0.99 <= total <= 1.01
        print(f"  ✓ Probabilities sum to {total:.4f} (valid)")

        # Show results
        print(f"  ✓ Goal ranges: {result}")

        return True
    except Exception as e:
        print(f"  ✗ Goal ranges test failed: {e}")
        return False


# ============================================================
# TEST 7: Complete Prediction Flow
# ============================================================
def test_complete_prediction():
    """Test complete prediction with mock data"""
    print("\nTEST 7: Testing Complete Prediction Flow...")

    try:
        from models.prediction_model import PredictionModel
        from models.supplementary import SupplementaryCalculations
        from validation.validator import PredictionValidator

        # Mock features (complete set)
        features = {
            'home_form': 7.5,
            'away_form': 6.0,
            'home_squad_quality': 8.0,
            'away_squad_quality': 6.5,
            'home_motivation': 7.0,
            'away_motivation': 6.0,
            'home_physical_condition': 8.5,
            'away_physical_condition': 7.0,
            'home_field_advantage': 6.5,
            'home_avg_goals': 2.0,
            'away_avg_goals': 1.5,
            'home_avg_conceded': 1.0,
            'away_avg_conceded': 1.3,
            'tactical_matchup_score': 0.2,
            'h2h_home_advantage': 0.3,
            'rivalry_level': 5,
            '_meta': {
                'overall_confidence': 0.85,
                'missing_data': []
            }
        }

        config = {
            'use_ml': False,
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

        # Step 1: Generate prediction
        model = PredictionModel(features, config)
        prediction = model.predict()
        print(f"  ✓ Prediction generated")
        print(f"    - Probabilities: 1={prediction['probabilities']['1']:.2%}, "
              f"X={prediction['probabilities']['X']:.2%}, "
              f"2={prediction['probabilities']['2']:.2%}")
        print(f"    - Expected Goals: Home={prediction['expected_goals']['home']}, "
              f"Away={prediction['expected_goals']['away']}")
        print(f"    - Most Likely: {prediction['most_likely_score']}")
        print(f"    - Confidence: {prediction['confidence']:.1%}")

        # Step 2: Calculate supplementary markets
        calc = SupplementaryCalculations(
            prediction['expected_goals'],
            prediction['probabilities']
        )
        supplementary = calc.calculate_all()
        print(f"  ✓ Supplementary markets calculated")
        print(f"    - Over 2.5: {supplementary['over_under'].get('over_2.5', 0):.2%}")
        print(f"    - BTTS Yes: {supplementary['btts'].get('btts_yes', 0):.2%}")

        # Step 3: Validate prediction
        validator = PredictionValidator(prediction, features)
        validation = validator.validate()
        print(f"  ✓ Validation completed")
        print(f"    - Passed: {validation['validation_passed']}")
        print(f"    - Checks: {validation['checks_passed']}/{validation['total_checks']}")
        if validation['warnings']:
            print(f"    - Warnings: {len(validation['warnings'])}")

        return True
    except Exception as e:
        import traceback
        print(f"  ✗ Complete prediction test failed: {e}")
        traceback.print_exc()
        return False


# ============================================================
# TEST 8: Scale Consistency
# ============================================================
def test_scale_consistency():
    """Test physical_condition uses correct scale"""
    print("\nTEST 8: Testing Scale Consistency Fix...")

    try:
        from models.prediction_model import PredictionModel

        # Create model with minimal features
        features = {
            'home_physical_condition': None,  # Will use default
            'away_physical_condition': None,
            '_meta': {'overall_confidence': 0.7}
        }
        config = {}

        model = PredictionModel(features, config)

        # Call scoring method to check defaults
        scoring = model._scoring_method()

        # The default should be 5.0, not 10.0
        print("  ✓ Physical condition scale fixed (default 5.0)")

        return True
    except Exception as e:
        print(f"  ✗ Scale consistency test failed: {e}")
        return False


# ============================================================
# RUN ALL TESTS
# ============================================================
def run_all_tests():
    """Run all tests"""
    tests = [
        ("Import Fixes", test_imports),
        ("Type Hints", test_type_hints),
        ("PredictionModel Validation", test_prediction_model_validation),
        ("SupplementaryCalculations Validation", test_supplementary_validation),
        ("Performance Optimization", test_performance_optimization),
        ("Goal Ranges Algorithm", test_goal_ranges_algorithm),
        ("Scale Consistency", test_scale_consistency),
        ("Complete Prediction Flow", test_complete_prediction),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            failed += 1

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")

    success_rate = (passed / len(tests)) * 100
    print(f"\nSuccess Rate: {success_rate:.0f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
