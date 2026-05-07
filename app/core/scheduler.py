"""app/core/scheduler.py — APScheduler CRON jobs."""

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

scheduler = AsyncIOScheduler()


async def _render_keepalive_job():
    """Ping own health endpoint every 10 min to prevent Render cold starts."""
    url = f"{settings.BASE_URL}/health"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
        print(f"[SCHEDULER] Keep-alive ping sent → {url} ({response.status_code})")
    except Exception as exc:
        print(f"[SCHEDULER] Keep-alive ping failed → {url} | error: {exc}")


def start_scheduler():
    """Register and start all CRON jobs. Call from app lifespan."""
    scheduler.add_job(
        _render_keepalive_job,
        trigger=IntervalTrigger(minutes=10),
        id="render_keepalive",
        replace_existing=True,
    )
    scheduler.start()
    print("[SCHEDULER] Scheduler started")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    print("[SCHEDULER] Scheduler stopped")
