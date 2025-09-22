# Metrics & health APIs

from fastapi import APIRouter
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    "elara_api_request_count",
    "Total number of requests processed",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "elara_api_request_latency_seconds",
    "Latency in seconds for processing requests",
    ["method", "endpoint"]
)

ERROR_COUNT = Counter(
    "elara_api_error_count",
    "Total number of errors encountered",
    ["method", "endpoint", "http_status"]
)

@router.get("/metrics")
async def metrics():
    # Return latest metrics data in Prometheus format
    return generate_latest()

# Optional helpers for updating metrics.
def record_request(method: str, endpoint: str, status_code: int, latency: float, error: bool = False):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status_code)).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
    if error:
        ERROR_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status_code)).inc()
