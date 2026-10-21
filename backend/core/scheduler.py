"""Background scheduler for periodic data refresh."""
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from core.data_refresh import refresh_pipeline

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_data_refresh():
    """Scheduled task to refresh data periodically."""
    logger.info("⏰ Scheduled data refresh triggered")
    result = refresh_pipeline.run_full_pipeline()

    if result["status"] == "completed_successfully":
        logger.info("✅ Scheduled refresh completed successfully")
    else:
        logger.warning(f"⚠️ Scheduled refresh completed with status: {result['status']}")


def start_scheduler():
    """Start the background scheduler."""
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    try:
        # Schedule daily refresh at 2 AM UTC (9 AM Baghdad time)
        scheduler.add_job(
            scheduled_data_refresh,
            trigger=CronTrigger(hour=2, minute=0),  # 2 AM UTC daily
            id="daily_data_refresh",
            name="Daily Data Refresh",
            replace_existing=True,
            misfire_grace_time=900,  # 15 min grace period
        )

        # Also add a job every 4 hours for intra-day updates
        scheduler.add_job(
            scheduled_data_refresh,
            trigger=CronTrigger(minute=0, hour="*/4"),  # Every 4 hours
            id="intraday_data_refresh",
            name="Intraday Data Refresh",
            replace_existing=True,
            misfire_grace_time=300,  # 5 min grace period
        )

        scheduler.start()
        logger.info("✅ Scheduler started with 2 jobs:")
        logger.info("  - Daily refresh at 02:00 UTC (09:00 Baghdad)")
        logger.info("  - Intraday refresh every 4 hours")

    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped")


def get_scheduler_status() -> dict:
    """Get the current scheduler status."""
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ],
        "last_refresh_status": refresh_pipeline.get_status(),
    }
