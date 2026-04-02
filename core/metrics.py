from prometheus_client import Counter, Histogram, Gauge

REQUEST_DURATION_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "endpoint"],
    buckets=REQUEST_DURATION_BUCKETS,
)

events_provider_requests_total = Counter(
    "events_provider_requests_total",
    "Total number of requests to event provider",
    ["endpoint", "status"],
)

events_provider_request_duration_seconds = Histogram(
    "events_provider_request_duration_seconds",
    "Duration of requests to event provider in seconds",
    ["endpoint"],
    buckets=REQUEST_DURATION_BUCKETS,
)

tickets_created_total = Counter(
    "tickets_created_total", "Total number of created tickets"
)

tickets_cancelled_total = Counter(
    "tickets_cancelled_total", "Total number of cancelled tickets"
)

events_total = Gauge("events_total", "Total number of events in DB")

cache_hits_total = Counter("cache_hits_total", "Total number of cache hits for seats")

cache_misses_total = Counter(
    "cache_misses_total", "Total number of cache misses for seats"
)
