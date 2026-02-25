from django.utils.dateparse import parse_datetime
from core.models import SyncState, Place, Event
from django.utils import timezone
from datetime import timezone as dt_timezone, timedelta
import os
import logging
from core.clients.events_provider import EventsProviderClient, EventsPaginator
from uuid import UUID


PROVIDER_TZ = dt_timezone(timedelta(hours=3))

logger = logging.getLogger(__name__)

PLACE_UPDATE_FIELDS = [
    "name",
    "city",
    "address",
    "seats_pattern",
    "changed_at",
    "created_at",
]

def bulk_upsert_places_from_events(events):
    places_data = {}
    for event in events:
        place = event.get("place")
        if not place:
            continue
        place_id = place.get("id")
        if not place_id:
            place_id = None
        try:
            if not isinstance(place_id, UUID):
                place_id = UUID(str(place_id))
        except (ValueError, TypeError):
            logger.warning("Invalid place_id=%r, skip place", place.get("id"))
            continue
 
        if place_id:
            places_data[place_id] = place

    if not places_data:
        return {}

    place_ids = list(places_data.keys())
    existing_places = Place.objects.in_bulk(place_ids)

    to_create = []
    to_update = []

    for place_id, place in places_data.items():
        data = {
            "name": place.get("name", ""),
            "city": place.get("city", ""),
            "address": place.get("address", ""),
            "seats_pattern": place.get("seats_pattern", ""),
            "changed_at": parse_datetime(place["changed_at"]) if place.get("changed_at") else None,
            "created_at": parse_datetime(place["created_at"]) if place.get("created_at") else None,
        }

        if place_id in existing_places:
            obj = existing_places[place_id]
            obj.name = data["name"]
            obj.city = data["city"]
            obj.address = data["address"]
            obj.seats_pattern = data["seats_pattern"]
            obj.changed_at = data["changed_at"]
            obj.created_at = data["created_at"]
            to_update.append(obj)
        else:
            to_create.append(
                Place(
                    id=place_id,
                    name=data["name"],
                    city=data["city"],
                    address=data["address"],
                    seats_pattern=data["seats_pattern"],
                    changed_at=data["changed_at"],
                    created_at=data["created_at"],
                )
            )

    if to_create:
        Place.objects.bulk_create(to_create, batch_size=500)

    if to_update:
        Place.objects.bulk_update(to_update, fields=PLACE_UPDATE_FIELDS, batch_size=500)

    return Place.objects.in_bulk(place_ids)



def upsert_event(event, place_obj):
    event_id = event["id"]
    default_data_event = {
        "name": event.get("name", ""),
        "place": place_obj,
        "event_time": parse_datetime(event["event_time"]) if event.get("event_time") else None,
        "registration_deadline": parse_datetime(event["registration_deadline"]) if event.get("registration_deadline") else None,
        "status": event.get("status", ""),
        "number_of_visitors": event.get("number_of_visitors", 0),
        "changed_at": parse_datetime(event["changed_at"]) if event.get("changed_at") else None,
        "created_at": parse_datetime(event["created_at"]) if event.get("created_at") else None,
        "status_changed_at": parse_datetime(event["status_changed_at"]) if event.get("status_changed_at") else None,
    }

    new_event, event_created = Event.objects.update_or_create(
        id=event_id,
        defaults=default_data_event
    )
    return new_event


def sync_events():
    sync_state, created = SyncState.objects.get_or_create(id=1)
    last_changed_at = sync_state.last_changed_at

    if not last_changed_at:
        changed_at = "2000-01-01"
    else:
        dt_in_provider_tz = timezone.localtime(last_changed_at, PROVIDER_TZ)
        changed_at = dt_in_provider_tz.date().isoformat()

    client = EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
    )

    sync_state.sync_status = SyncState.StatusChoices.RUNNING
    sync_state.save()

    logger.info("sync_events started: changed_at=%s last_changed_at=%s", changed_at, last_changed_at)

    processed = 0
    max_changed_at = None

    try:
        paginator = EventsPaginator(client, changed_at)
        while True:
            results, next_url = paginator.fetch_page(cursor=paginator.cursor)

            paginator.cursor = next_url

            if not results:
                if not next_url:
                    break
                continue

            places_by_id = bulk_upsert_places_from_events(results)
            for event in results:
                place = event.get("place")
                if not place:
                    logger.warning("Event id=%r has no place, skip", event.get("id"))
                    continue
                place_id = place.get("id")
                if not place_id:
                    logger.warning("Event id=%r has no place_id, skip", event.get("id"))
                    continue
                try:
                    if not isinstance(place_id, UUID):
                        place_id = UUID(str(place_id))
                except (ValueError, TypeError):
                    logger.warning("Invalid place_id=%r in event id=%r, skip", place.get("id"), event.get("id"))
                    continue
                place_obj = places_by_id.get(place_id)
                if not place_obj:
                    logger.warning("Place not found after bulk upsert: place_id=%r event_id=%r, skip", place_id, event.get("id"))
                    continue

                upsert_event(event, place_obj)
                processed += 1

                event_changed_at = parse_datetime(event["changed_at"]) if event.get("changed_at") else None
                if event_changed_at is not None:
                    if max_changed_at is None or event_changed_at > max_changed_at:
                        max_changed_at = event_changed_at

            if not next_url:
                break

        if max_changed_at:
            sync_state.last_changed_at = max_changed_at

        sync_state.last_sync_time = timezone.now()
        sync_state.sync_status = SyncState.StatusChoices.SUCCESS
        sync_state.save()

        logger.info(
            "sync_events finished: status=success processed=%s max_changed_at=%s",
            processed,
            max_changed_at,
        )

    except Exception:
        sync_state.sync_status = SyncState.StatusChoices.FAILED
        sync_state.last_sync_time = timezone.now()
        sync_state.save()

        logger.exception("sync_events failed: processed=%s", processed)
        raise