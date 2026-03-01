import os
from core.clients.events_provider import EventsProviderClient
from core.models import Event
from rest_framework.exceptions import NotFound, ValidationError
from django.core.cache import cache


CACH_TTL = 30

def get_seats(event_id) -> dict:
    """Получаем словарь event_id - seats"""
    try:
        event = Event.objects.select_related("place").get(id=event_id)
    except Event.DoesNotExist:
        raise NotFound("Event not found")

    if event.status != 'published':
        raise ValidationError("Event is not published")
    
    cache_key = f'seats_for:{event_id}'
    cached_event = cache.get(cache_key)
    
    if cached_event is not None:
        return{'event_id': event_id, 'available_seats': cached_event}
    client = EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
       )
    seats = client.seats(event_id)
    cache.set(cache_key, seats, timeout=CACH_TTL)
    return{'event_id': event_id, 'available_seats': seats}