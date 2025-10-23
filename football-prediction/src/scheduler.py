"""Automated scheduler for prediction system"""

import logging
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List

from .pipeline import MatchPredictionPipeline
from .learning import PostMatchAnalyzer, analyze_model_performance

logger = logging.getLogger(__name__)


class AutomatedScheduler:
    """
    Automated job scheduler for prediction system

    Schedules:
    - H-24: Initial analysis 24 hours before match
    - H-3: Updated analysis 3 hours before match
    - Post-match: Analysis after match completion
    - Daily performance review
    """

    def __init__(self):
        """Initialize scheduler"""
        self.running = False

    def setup_schedules(self):
        """Configure all scheduled jobs"""

        # Daily H-24 analysis (morning)
        schedule.every().day.at("10:00").do(self.run_h24_analysis)

        # Check for matches needing H-3 updates (every 10 minutes)
        schedule.every(10).minutes.do(self.check_upcoming_matches)

        # Post-match analysis (hourly)
        schedule.every().hour.do(self.analyze_finished_matches)

        # Daily performance review (evening)
        schedule.every().day.at("22:00").do(self.daily_performance_review)

        logger.info("✅ Scheduler configured successfully")
        logger.info("Jobs scheduled:")
        logger.info("  - H-24 analysis: Daily at 10:00")
        logger.info("  - H-3 updates: Every 10 minutes")
        logger.info("  - Post-match analysis: Hourly")
        logger.info("  - Performance review: Daily at 22:00")

    def run_h24_analysis(self):
        """Run H-24 analysis for tomorrow's matches"""
        logger.info("Starting H-24 analysis...")

        tomorrow = datetime.now() + timedelta(days=1)
        matches = self._get_matches_for_date(tomorrow.date())

        logger.info(f"Found {len(matches)} matches for {tomorrow.date()}")

        for match in matches:
            try:
                asyncio.run(self._run_prediction(match.id))
                logger.info(f"✅ H-24 analysis complete for match {match.id}")
            except Exception as e:
                logger.error(f"❌ H-24 analysis failed for match {match.id}: {e}")

        logger.info(f"H-24 analysis complete: {len(matches)} matches processed")

    def check_upcoming_matches(self):
        """Check matches in next 3 hours needing updates"""
        logger.debug("Checking upcoming matches...")

        now = datetime.now()
        window_end = now + timedelta(hours=3)

        matches = self._get_matches_in_window(now, window_end)

        for match in matches:
            # Check if already analyzed recently
            last_pred = self._get_latest_prediction(match.id)

            if not last_pred:
                # No prediction yet - create one
                logger.info(f"Creating prediction for match {match.id} (H-3)")
                asyncio.run(self._run_prediction(match.id))

            else:
                # Check if needs update
                age_hours = (now - last_pred.created_at).total_seconds() / 3600

                if age_hours > 1:  # Update if older than 1 hour
                    logger.info(f"Updating prediction for match {match.id} (H-{age_hours:.1f})")
                    asyncio.run(self._run_prediction(match.id))

    def analyze_finished_matches(self):
        """Analyze recently finished matches"""
        logger.info("Checking for finished matches...")

        finished = self._get_recently_finished_matches()

        logger.info(f"Found {len(finished)} recently finished matches")

        for match in finished:
            # Check if already analyzed
            pred = self._get_latest_prediction(match.id)

            if not pred:
                logger.warning(f"No prediction found for finished match {match.id}")
                continue

            # Check if result already exists
            from database import get_db
            with get_db() as db:
                from database.models import PredictionResult
                existing = db.query(PredictionResult).filter_by(
                    prediction_id=pred.id
                ).first()

                if existing:
                    continue  # Already analyzed

            # Analyze
            try:
                analyzer = PostMatchAnalyzer(pred.id)
                result = analyzer.analyze()

                if result['prediction_accuracy']['correct']:
                    logger.info(f"✅ Match {match.id}: Prediction CORRECT")
                else:
                    logger.info(
                        f"❌ Match {match.id}: Prediction INCORRECT "
                        f"(predicted {result['prediction_accuracy']['predicted']}, "
                        f"actual {result['prediction_accuracy']['actual']})"
                    )

            except Exception as e:
                logger.error(f"Post-match analysis failed for match {match.id}: {e}")

    def daily_performance_review(self):
        """Daily performance summary"""
        logger.info("Running daily performance review...")

        try:
            performance = analyze_model_performance(last_n_predictions=100)

            logger.info("═" * 60)
            logger.info("DAILY PERFORMANCE REVIEW")
            logger.info("═" * 60)
            logger.info(f"Sample Size: {performance['sample_size']}")
            logger.info(f"Accuracy: {performance['overall_accuracy']:.1%}")
            logger.info(f"Avg Brier Score: {performance['avg_brier_score']:.4f}")
            logger.info(f"Simulated ROI: {performance['simulated_roi']:.2%}")

            if 'accuracy_by_outcome' in performance:
                logger.info("\nAccuracy by Outcome:")
                for outcome, stats in performance['accuracy_by_outcome'].items():
                    logger.info(
                        f"  {outcome}: {stats['accuracy']:.1%} ({stats['count']} predictions)"
                    )

            logger.info("═" * 60)

        except Exception as e:
            logger.error(f"Performance review failed: {e}")

    async def _run_prediction(self, match_id: int):
        """Run prediction for a match"""
        pipeline = MatchPredictionPipeline(match_id)
        await pipeline.run(save_formats=['db', 'json'])

    def _get_matches_for_date(self, date) -> List:
        """Get matches for specific date"""
        from database import get_db

        with get_db() as db:
            from database.models import Match
            from sqlalchemy import func

            return db.query(Match).filter(
                func.date(Match.match_datetime) == date,
                Match.status == 'NS'  # Not started
            ).all()

    def _get_matches_in_window(self, start, end) -> List:
        """Get matches in time window"""
        from database import get_db

        with get_db() as db:
            from database.models import Match

            return db.query(Match).filter(
                Match.match_datetime.between(start, end),
                Match.status == 'NS'
            ).all()

    def _get_recently_finished_matches(self) -> List:
        """Get matches finished in last 2 hours"""
        from database import get_db

        cutoff = datetime.now() - timedelta(hours=2)

        with get_db() as db:
            from database.models import Match

            return db.query(Match).filter(
                Match.status == 'FT',
                Match.match_datetime >= cutoff
            ).all()

    def _get_latest_prediction(self, match_id: int):
        """Get latest prediction for a match"""
        from database import get_db

        with get_db() as db:
            from database.models import Prediction

            return db.query(Prediction).filter_by(
                match_id=match_id
            ).order_by(Prediction.created_at.desc()).first()

    def run(self):
        """Start scheduler main loop"""
        logger.info("🚀 Starting automated scheduler...")
        self.running = True

        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop(self):
        """Stop scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    """Run scheduler as standalone service"""
    import signal

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 60)
    print("FOOTBALL PREDICTION SYSTEM - AUTOMATED SCHEDULER")
    print("=" * 60 + "\n")

    scheduler = AutomatedScheduler()
    scheduler.setup_schedules()

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        print("\n\nShutting down gracefully...")
        scheduler.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")


if __name__ == "__main__":
    main()
