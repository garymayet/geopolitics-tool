"""
Scheduled tasks:
  - Fetch all feeds every N minutes
  - Cleanup old articles daily
"""

import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from feeds import FEEDS
from fetcher import fetch_all
from db import cleanup_old

logger = logging.getLogger("scheduler")

FETCH_INTERVAL_MIN = int(os.environ.get("FETCH_INTERVAL_MIN", "15"))
CLEANUP_RETENTION_DAYS = int(os.environ.get("CLEANUP_DAYS", "7"))

scheduler = BackgroundScheduler(daemon=True)


def scheduled_fetch():
    logger.info("=== Scheduled fetch starting ===")
    try:
        result = fetch_all(FEEDS)
        logger.info(
            f"Scheduled fetch complete: {result['feeds_ok']}/{result['feeds_total']} OK, "
            f"{result['articles_new']} new articles"
        )
    except Exception as e:
        logger.error(f"Scheduled fetch failed: {e}")


def scheduled_cleanup():
    logger.info("=== Scheduled cleanup starting ===")
    try:
        removed = cleanup_old(days=CLEANUP_RETENTION_DAYS)
        logger.info(f"Cleanup removed {removed} old articles")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


def start_scheduler():
    scheduler.add_job(
        scheduled_fetch,
        trigger=IntervalTrigger(minutes=FETCH_INTERVAL_MIN),
        id="fetch_all",
        name=f"Fetch all feeds every {FETCH_INTERVAL_MIN}min",
        replace_existing=True,
    )

    scheduler.add_job(
        scheduled_cleanup,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup",
        name="Daily cleanup at 03:00 UTC",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started — fetch every {FETCH_INTERVAL_MIN}min, "
        f"cleanup daily (retain {CLEANUP_RETENTION_DAYS} days)"
    )
