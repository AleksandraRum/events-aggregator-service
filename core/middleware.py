import time
from core.metrics import http_request_duration_seconds, http_requests_total


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start_time

        http_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=str(response.status_code),
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.path,
        ).observe(duration)

        return response
