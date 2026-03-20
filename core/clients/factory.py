import os

from core.clients.events_provider import EventsProviderClient


def get_events_provider_client():
    return EventsProviderClient(
        base_url=os.environ["EVENTS_PROVIDER_BASE_URL"],
        api_key=os.environ["EVENTS_PROVIDER_API_KEY"],
    )
