# Monitoring and Metrics System

This system provides comprehensive monitoring and metrics collection for the Telegram Bot summarization service, including DistilBERT preprocessing metrics and API usage statistics.

## Features

- Real-time metrics collection for:
  - DistilBERT preprocessing (token count, processing time)
  - API performance (Gemini, TTS)
  - Error rates and success rates
  - Cost tracking
- Rolling window metrics storage (default: 1000 most recent entries)
- JSON line logging for persistent storage
- Admin API endpoints for metrics access

## API Endpoints

All endpoints require HTTP Basic Authentication with admin credentials.

```
GET /metrics/performance
```
Returns performance metrics including:
- Response times (mean, p95, max)
- Token counts (mean, max)
- Error rates
- Success rates

```
GET /metrics/api
```
Returns API usage statistics including:
- Daily summary counts
- Daily audio minutes
- Per-API performance metrics
- Cost tracking

```
GET /metrics/logs?limit=100
```
Returns recent log entries in JSON format (default: last 100 entries)

## Usage Example

```python
from src.logging import MetricsCollector

# Get the global metrics collector instance
metrics = MetricsCollector()

# Log text processing metrics
metrics.log_processing_metrics(
    text="Sample text",
    response_time=1.5,
    success=True,
    error_count=0
)

# Log API call metrics
metrics.log_api_call(
    api_name="gemini",
    response_time=2.1,
    success=True,
    cost=0.001
)

# Get performance stats
stats = metrics.get_performance_stats()
```

## Environment Variables

- `ADMIN_USERNAME`: Admin username for metrics API (default: "admin")
- `ADMIN_PASSWORD`: Admin password for metrics API (required)

## Data Storage

Metrics are stored in:
- Memory: Rolling window of recent metrics (configurable size)
- Disk: JSON line format in `data/metrics.jsonl`
