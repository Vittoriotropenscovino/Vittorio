"""Main prediction pipeline - Orchestrates complete prediction workflow"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from data_collection import DataCollectionOrchestrator, MatchAnalysisInput
from processing import DataProcessor
from models import PredictionModel, SupplementaryCalculations
from validation import PredictionValidator
from output import ReportGenerator, PredictionOutput, save_prediction

logger = logging.getLogger(__name__)


class MatchPredictionPipeline:
    """
    Complete automated prediction pipeline

    Coordinates:
    1. Data collection from multiple sources
    2. Feature engineering and processing
    3. Prediction generation (multiple methods)
    4. Validation and quality assurance
    5. Report generation and storage
    """

    def __init__(self, match_id: int):
        """
        Initialize pipeline for a match

        Args:
            match_id: ID of match to predict
        """
        self.match_id = match_id
        self.config = self._load_config()

    async def run(self, save_formats: list = ['json', 'db']) -> PredictionOutput:
        """
        Execute complete prediction pipeline

        Args:
            save_formats: List of formats to save ('json', 'db', 'markdown')

        Returns:
            PredictionOutput object with complete prediction
        """
        try:
            logger.info(f"[MATCH {self.match_id}] Starting prediction pipeline...")

            # STEP 1: Fetch match metadata
            logger.info("[STEP 1/6] Fetching match metadata...")
            match_input = await self._fetch_match_metadata()

            # STEP 2: Collect data from all sources
            logger.info("[STEP 2/6] Collecting data from sources...")
            collector = DataCollectionOrchestrator(match_input)
            raw_data = await collector.collect_all_data()

            # Check data quality
            if raw_data['_meta']['overall_confidence'] < 0.50:
                raise ValueError(
                    f"Insufficient data quality "
                    f"({raw_data['_meta']['overall_confidence']:.1%}) - aborting"
                )

            # STEP 3: Process features
            logger.info("[STEP 3/6] Processing features...")
            processor = DataProcessor(raw_data)
            features = processor.process()
            features['_meta'] = raw_data['_meta']
            features['_odds'] = raw_data.get('odds', {}).get('data')

            # STEP 4: Generate prediction
            logger.info("[STEP 4/6] Generating prediction...")
            model = PredictionModel(features, self.config)
            prediction = model.predict()

            # Calculate supplementary markets
            supp_calc = SupplementaryCalculations(
                prediction['expected_goals'],
                prediction['probabilities']
            )
            prediction['supplementary'] = supp_calc.calculate_all()

            # STEP 5: Validate prediction
            logger.info("[STEP 5/6] Validating prediction...")
            validator = PredictionValidator(prediction, features)
            validation = validator.validate()

            if not validation['validation_passed']:
                logger.warning(
                    f"Validation issues detected: {len(validation['errors'])} errors, "
                    f"{len(validation['warnings'])} warnings"
                )

            # STEP 6: Generate output
            logger.info("[STEP 6/6] Generating output...")

            # Store processed features for output
            raw_data['processed_features'] = features

            generator = ReportGenerator(
                match_input,
                raw_data,
                prediction,
                validation
            )
            output = generator.generate()

            # Save in requested formats
            for format in save_formats:
                save_prediction(output, format=format)

            logger.info(
                f"[MATCH {self.match_id}] ✅ Pipeline completed successfully!\n"
                f"  Confidence: {output.confidence:.1%}\n"
                f"  Most Likely: {output.most_likely_result} ({output.most_likely_score})\n"
                f"  Probabilities: 1={output.probabilities['1']:.1%} "
                f"X={output.probabilities['X']:.1%} 2={output.probabilities['2']:.1%}"
            )

            return output

        except Exception as e:
            logger.error(f"[MATCH {self.match_id}] ❌ Pipeline failed: {e}")
            raise

    async def _fetch_match_metadata(self) -> MatchAnalysisInput:
        """Fetch basic match information"""
        from data_collection.api_clients import APIFootballClient

        client = APIFootballClient()

        try:
            data = await client.get_fixture_async(self.match_id)

            if not data.get('response'):
                raise ValueError(f"Match {self.match_id} not found")

            fixture = data['response'][0]

            match_input = MatchAnalysisInput(
                match_id=self.match_id,
                home_team_id=fixture['teams']['home']['id'],
                away_team_id=fixture['teams']['away']['id'],
                match_datetime=fixture['fixture']['date'],
                competition_id=fixture['league']['id']
            )

            logger.info(
                f"Match loaded: {fixture['teams']['home']['name']} vs "
                f"{fixture['teams']['away']['name']} "
                f"({fixture['league']['name']})"
            )

            return match_input

        finally:
            await client.close()

    def _load_config(self) -> dict:
        """Load model configuration"""
        import os

        return {
            "use_ml": os.getenv('ENABLE_ML', 'false').lower() == 'true',
            "ml_model_path": os.getenv('ML_MODEL_PATH', 'models_ml/match_predictor_v1.pkl'),
            "weights": {
                'form': float(os.getenv('WEIGHT_FORM', '0.25')),
                'squad_quality': float(os.getenv('WEIGHT_SQUAD_QUALITY', '0.20')),
                'motivation': float(os.getenv('WEIGHT_MOTIVATION', '0.15')),
                'physical_condition': float(os.getenv('WEIGHT_PHYSICAL_CONDITION', '0.15')),
                'home_advantage': float(os.getenv('WEIGHT_HOME_ADVANTAGE', '0.10')),
                'tactical': float(os.getenv('WEIGHT_TACTICAL', '0.10')),
                'psychological': float(os.getenv('WEIGHT_PSYCHOLOGICAL', '0.05')),
            }
        }


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

async def predict_match(match_id: int) -> PredictionOutput:
    """
    Quick prediction for a single match

    Args:
        match_id: Match ID to predict

    Returns:
        PredictionOutput object
    """
    pipeline = MatchPredictionPipeline(match_id)
    return await pipeline.run()


async def predict_multiple(match_ids: list) -> list:
    """
    Predict multiple matches in parallel

    Args:
        match_ids: List of match IDs

    Returns:
        List of PredictionOutput objects
    """
    tasks = [predict_match(mid) for mid in match_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = []
    failed = []

    for mid, result in zip(match_ids, results):
        if isinstance(result, Exception):
            failed.append({'match_id': mid, 'error': str(result)})
            logger.error(f"Match {mid} failed: {result}")
        else:
            successful.append(result)

    logger.info(
        f"Batch prediction complete: {len(successful)} successful, {len(failed)} failed"
    )

    return successful


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

async def main():
    """CLI entry point"""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <match_id>")
        print("Example: python pipeline.py 1035480")
        sys.exit(1)

    match_id = int(sys.argv[1])

    print(f"\n{'='*60}")
    print(f"FOOTBALL MATCH PREDICTION SYSTEM v3.0")
    print(f"{'='*60}\n")

    try:
        result = await predict_match(match_id)

        print(f"\n{'='*60}")
        print(f"PREDICTION: {result.home_team} vs {result.away_team}")
        print(f"{'='*60}\n")

        print(f"🎯 Most Likely: {result.most_likely_result} ({result.most_likely_score})")
        print(f"\n📊 Probabilities:")
        print(f"   Home Win: {result.probabilities['1']:.1%}")
        print(f"   Draw:     {result.probabilities['X']:.1%}")
        print(f"   Away Win: {result.probabilities['2']:.1%}")

        print(f"\n⚽ Expected Goals:")
        print(f"   {result.home_team}: {result.expected_goals['home']}")
        print(f"   {result.away_team}: {result.expected_goals['away']}")

        print(f"\n📈 Confidence: {result.confidence:.1%} ({result.data_quality})")

        if result.value_bets:
            print(f"\n💰 Value Bets:")
            for vb in result.value_bets:
                print(f"   {vb['outcome']}: {vb['edge']:.1%} edge @ {vb['odds']}")

        print(f"\n{'='*60}\n")
        print(f"✅ Prediction saved successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
