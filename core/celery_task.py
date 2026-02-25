from celery import shared_task
from core.services.sync import sync_events
import logging

logger = logging.getLogger(__name__)

@shared_task()
def sync_events_task():
    try:
        sync_events()
    except Exception:
        logger.exception("sync_events_task failed")
        raise