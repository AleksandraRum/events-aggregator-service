import requests


class CapashinoClient:
    def __init__(self, capashino_base_url, api_key):
        self.capashino_base_url = capashino_base_url
        self.api_key = api_key

    def send_notification(self, message, reference_id, idempotency_key):
        headers = {"x-api-key": self.api_key}
        url = f'{self.capashino_base_url}/api/notifications'
        payload = {}
        payload["message"] = message
        payload["reference_id"] = reference_id
        payload["idempotency_key"] = idempotency_key

        response = requests.post(
            url = url,
            headers=headers,
            json = payload,
            timeout = 10
        )
        response.raise_for_status()
        return response.json()
