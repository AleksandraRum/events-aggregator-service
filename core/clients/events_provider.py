import requests
import time
from core.metrics import (
    events_provider_request_duration_seconds,
    events_provider_requests_total,
)


class EventsProviderClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _request_with_metrics(
        self, url, endpoint, method, headers=None, params=None, json=None
    ):
        start_time = time.monotonic()
        response = method(
            url=url, params=params, headers=headers, json=json, timeout=60
        )
        duration = time.monotonic() - start_time

        events_provider_requests_total.labels(
            endpoint=endpoint,
            status=str(response.status_code),
        ).inc()

        events_provider_request_duration_seconds.labels(
            endpoint=endpoint,
        ).observe(duration)

        response.raise_for_status()

        return response

    def events(self, changed_at, cursor=None):
        metrics_endpoint = "/events"
        headers = {"x-api-key": self.api_key}
        method = requests.get
        if cursor:
            url = cursor
            response = self._request_with_metrics(
                url=url, endpoint=metrics_endpoint, method=method, headers=headers
            )
        else:
            url = f"{self.base_url}/api/events/"
            params = {"changed_at": changed_at}
            response = self._request_with_metrics(
                url=url,
                endpoint=metrics_endpoint,
                method=method,
                headers=headers,
                params=params,
            )
        return response.json()

    def register(self, event_id, first_name, last_name, email, seat):
        method = requests.post
        metrics_endpoint = "/registration"
        headers = {"x-api-key": self.api_key}
        url = f"{self.base_url}/api/events/{event_id}/register/"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        response = self._request_with_metrics(
            url=url,
            endpoint=metrics_endpoint,
            method=method,
            headers=headers,
            json=payload,
        )
        data = response.json()
        return data["ticket_id"]

    def unregister(self, event_id, ticket_id):
        method = requests.delete
        metrics_endpoint = "/unregistration"
        headers = {"x-api-key": self.api_key}
        url = f"{self.base_url}/api/events/{event_id}/unregister/"
        payload = {"ticket_id": str(ticket_id)}
        response = self._request_with_metrics(
            url=url,
            endpoint=metrics_endpoint,
            method=method,
            headers=headers,
            json=payload,
        )
        data = response.json()
        return data["success"]

    def seats(self, event_id):
        method = requests.get
        metrics_endpoint = "/seats"
        headers = {"x-api-key": self.api_key}
        url = f"{self.base_url}/api/events/{event_id}/seats/"
        response = self._request_with_metrics(
            url=url, endpoint=metrics_endpoint, method=method, headers=headers
        )
        data = response.json()
        return data["seats"]


class EventsPaginator:
    def __init__(self, client, changed_at):
        self.client = client
        self.changed_at = changed_at
        self.cursor = None
        self.finished = False

    def fetch_page(self, cursor=None):
        if cursor:
            resp = self.client.events(changed_at=self.changed_at, cursor=cursor)
        else:
            resp = self.client.events(changed_at=self.changed_at)
        return (resp["results"], resp["next"])

    def __iter__(self):
        return self

    def __next__(self):
        if self.finished:
            raise StopIteration
        res, next_url = self.fetch_page(cursor=self.cursor)
        self.cursor = next_url
        if not next_url:
            self.finished = True
        if not res:
            raise StopIteration
        return res
