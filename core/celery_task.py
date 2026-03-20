import logging
import os

import requests
from django.utils import timezone

from celery import shared_task
from core.clients.capashino_client import CapashinoClient
from core.models import NotificationOutbox
from core.services.sync import sync_events

logger = logging.getLogger(__name__)


@shared_task()
def sync_events_task():
    try:
        sync_events()
    except Exception:
        logger.exception("sync_events_task failed")
        raise


def process_outbox_one_record(outbox_record):
    message = outbox_record.payload.get("message")
    reference_id = outbox_record.payload.get("reference_id")
    idempotency_key = str(outbox_record.id)
    if not message or not message.strip():
        logger.warning(f"Message of {outbox_record.id} is empty")
        return
    if not reference_id:
        logger.warning(f"Reference_id of {outbox_record.id} is empty")
        return

    logger.info(f"Record of {outbox_record.id} validated")
    client = CapashinoClient(
        capashino_base_url=os.environ["CAPASHINO_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
    )
    try:
        client.send_notification(message, reference_id, idempotency_key)
    except requests.exceptions.HTTPError as e:
        response = getattr(e, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code in (400, 401, 422):
            logger.warning(f"Data error for putbox {outbox_record.id}")
            return
        if 500 <= status_code < 600:
            logger.exception(f"Capashino error for outbox {outbox_record.id}")
            return
        if status_code == 409:
            logger.info(f"Duplicate notification for {outbox_record.id}")
    outbox_record.status = NotificationOutbox.StatusChoices.SENT
    outbox_record.sent_at = timezone.now()
    outbox_record.save(update_fields=["status", "sent_at"])

    # print("Record of {outbox_record.id} validated")


@shared_task()
def process_outbox_all_records():
    records = NotificationOutbox.objects.filter(
        status=NotificationOutbox.StatusChoices.PENDING
    ).order_by("created_at")[:100]
    for record in records:
        try:
            process_outbox_one_record(record)
        except Exception:
            logger.exception("process_outbox_one_record failed")
