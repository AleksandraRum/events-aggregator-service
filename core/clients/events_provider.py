import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class EventsProviderClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def events(self, changed_at, cursor=None):
        headers = {"x-api-key": self.api_key}
        if cursor:
            url = cursor
            response = requests.get(
                url = url,
                headers = headers,
                timeout=60
            )
            response.raise_for_status()
        else:
            url = f'{self.base_url}/api/events/'
            params = {}
            params["changed_at"] = changed_at

            response = requests.get(
                url = url,
                params = params,
                headers = headers,
                timeout=60
            )
            response.raise_for_status()
        return response.json()
    
    def register(self, event_id, first_name, last_name, email, seat):
        headers = {"x-api-key": self.api_key}
        url = f'{self.base_url}/api/events/{event_id}/register/'
        payload = {}
        payload["first_name"] = first_name
        payload["last_name"] = last_name
        payload["email"] = email
        payload["seat"] = seat

        response = requests.post(
            url = url,
            headers = headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["ticket_id"]
    
    def unregister(self, event_id, ticket_id):
        headers = {"x-api-key": self.api_key}
        url = f'{self.base_url}/api/events/{event_id}/unregister/'
        payload = {}
        payload["ticket_id"] = str(ticket_id)
        response = requests.delete(
            url = url,
            headers = headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["success"]

    
    def seats(self, event_id):
        headers = {"x-api-key": self.api_key}
        url = f'{self.base_url}/api/events/{event_id}/seats/'
        response = requests.get(
            url = url,
            headers = headers,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data['seats']


class EventsPaginator:
    def __init__(self, client, changed_at):
        self.client = client
        self.changed_at = changed_at
        self.cursor = None
        self.buffer = []
        self.index = 0
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
        if self.index >= len(self.buffer):
            res = self.fetch_page(cursor=self.cursor)
            self.cursor = res[1]
            self.buffer = res[0]
            self.index = 0
            if len(self.buffer) == 0 and self.cursor is None:
                self.finished = True
                raise StopIteration
        item = self.buffer[self.index]
        self.index += 1
        return item
        


    

    