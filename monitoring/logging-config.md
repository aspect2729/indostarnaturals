# Logging Configuration Guide

This guide explains the logging setup for IndoStar Naturals and how to use it effectively.

## Logging Architecture

The application uses structured JSON logging with the following components:

- **Python Logging**: Standard library logging with JSON formatter
- **CloudWatch Logs**: Centralized log aggregation in AWS
- **Log Groups**: Separate log groups for different services
- **Log Retention**: Configurable retention periods
- **Log Metrics**: Extract metrics from logs for alerting

## Log Levels

Use appropriate log levels:

- **DEBUG**: Detailed information for debugging (not in production)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause system failure

## Structured Logging Format

All logs are in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.services.order_service",
  "message": "Order created successfully",
  "request_id": "abc123",
  "user_id": 42,
  "order_id": 123,
  "duration_ms": 245,
  "environment": "production"
}
```

## Backend Logging

### Configuration

The backend logging is configured in `backend/app/core/logging_config.py`:

```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info", "request_id", "user_id"]:
                log_data[key] = value
        
        return json.dumps(log_data)
```

### Usage Examples

```python
import logging

logger = logging.getLogger(__name__)

# Simple log
logger.info("User logged in")

# Log with extra context
logger.info(
    "Order created",
    extra={
        "order_id": order.id,
        "user_id": user.id,
        "total_amount": float(order.final_amount),
        "request_id": request_id
    }
)

# Log errors with exception
try:
    process_payment()
except Exception as e:
    logger.error(
        "Payment processing failed",
        exc_info=True,
        extra={
            "order_id": order.id,
            "payment_provider": "razorpay"
        }
    )

# Log performance metrics
import time
start_time = time.time()
result = expensive_operation()
duration = time.time() - start_time

logger.info(
    "Operation completed",
    extra={
        "operation": "expensive_operation",
        "duration_ms": duration * 1000,
        "result_count": len(result)
    }
)
```

## Frontend Logging

### Console Logging

For development:

```typescript
console.log("User action:", { action: "add_to_cart", productId: 123 });
console.error("API error:", error);
```

### Production Logging

Send important events to backend:

```typescript
// src/utils/logger.ts
export const logEvent = async (
  level: "info" | "warning" | "error",
  message: string,
  context?: Record<string, any>
) => {
  if (import.meta.env.PROD) {
    try {
      await fetch("/api/v1/logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          level,
          message,
          context,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        }),
      });
    } catch (error) {
      // Fail silently - don't break user experience
      console.error("Failed to send log:", error);
    }
  } else {
    console.log(`[${level.toUpperCase()}]`, message, context);
  }
};

// Usage
logEvent("error", "Payment failed", {
  orderId: order.id,
  errorCode: error.code,
});
```

## CloudWatch Logs Setup

### Log Groups

Create log groups for each service:

```bash
# Backend API logs
aws logs create-log-group --log-group-name /ecs/indostar-backend

# Celery worker logs
aws logs create-log-group --log-group-name /ecs/indostar-celery-worker

# Celery beat logs
aws logs create-log-group --log-group-name /ecs/indostar-celery-beat

# Frontend logs (if using CloudWatch for frontend)
aws logs create-log-group --log-group-name /ecs/indostar-frontend
```

### Set Retention Policies

```bash
# Set 7-day retention for most logs
aws logs put-retention-policy \
  --log-group-name /ecs/indostar-backend \
  --retention-in-days 7

# Set 30-day retention for error logs
aws logs put-retention-policy \
  --log-group-name /ecs/indostar-backend-errors \
  --retention-in-days 30
```

### Log Insights Queries

Use CloudWatch Logs Insights for analysis:

#### Find All Errors

```
fields @timestamp, level, message, request_id, user_id
| filter level = "ERROR"
| sort @timestamp desc
| limit 100
```

#### Find Slow Requests

```
fields @timestamp, message, duration_ms, endpoint
| filter duration_ms > 2000
| sort duration_ms desc
| limit 50
```

#### Count Errors by Type

```
fields @timestamp, message
| filter level = "ERROR"
| stats count() by message
| sort count desc
```

#### Payment Failures

```
fields @timestamp, message, order_id, payment_provider
| filter message like /payment.*failed/
| sort @timestamp desc
```

#### External Service Failures

```
fields @timestamp, service, operation, error, retry_count
| filter alert_type = "external_service_failure"
| stats count() by service, operation
| sort count desc
```

## Log Aggregation

### ECS Log Configuration

Configure ECS tasks to send logs to CloudWatch:

```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/indostar-backend",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "backend"
    }
  }
}
```

### Log Streaming

Stream logs in real-time:

```bash
# Stream backend logs
aws logs tail /ecs/indostar-backend --follow

# Stream with filter
aws logs tail /ecs/indostar-backend --follow --filter-pattern "ERROR"

# Stream specific time range
aws logs tail /ecs/indostar-backend \
  --since 1h \
  --filter-pattern "order_id=123"
```

## Log Metrics

Extract metrics from logs for alerting:

### Create Metric Filters

```bash
# Order creation metric
aws logs put-metric-filter \
  --log-group-name /ecs/indostar-backend \
  --filter-name OrderCreated \
  --filter-pattern '[time, request_id, level=INFO, msg="Order created*"]' \
  --metric-transformations \
    metricName=OrdersCreated,\
    metricNamespace=IndoStar/Application,\
    metricValue=1

# Payment failure metric
aws logs put-metric-filter \
  --log-group-name /ecs/indostar-backend \
  --filter-name PaymentFailed \
  --filter-pattern '[time, request_id, level=ERROR, msg="*payment*failed*"]' \
  --metric-transformations \
    metricName=PaymentFailures,\
    metricNamespace=IndoStar/Application,\
    metricValue=1
```

## Best Practices

### 1. Always Include Context

```python
# Bad
logger.error("Payment failed")

# Good
logger.error(
    "Payment failed",
    extra={
        "order_id": order.id,
        "user_id": user.id,
        "payment_provider": "razorpay",
        "error_code": error.code,
        "request_id": request_id
    }
)
```

### 2. Use Request IDs

Always include request_id for tracing:

```python
from app.core.request_id_middleware import get_request_id

logger.info(
    "Processing request",
    extra={"request_id": get_request_id()}
)
```

### 3. Log Performance Metrics

```python
import time

start = time.time()
result = expensive_operation()
duration = time.time() - start

logger.info(
    "Operation completed",
    extra={
        "operation": "expensive_operation",
        "duration_ms": duration * 1000,
        "result_count": len(result)
    }
)
```

### 4. Don't Log Sensitive Data

```python
# Bad - logs password
logger.info(f"User login: {username} / {password}")

# Good - no sensitive data
logger.info(
    "User login attempt",
    extra={"username": username, "success": True}
)
```

### 5. Use Appropriate Log Levels

```python
# DEBUG - detailed debugging info (not in production)
logger.debug("Cache hit", extra={"key": cache_key})

# INFO - normal operations
logger.info("Order created", extra={"order_id": order.id})

# WARNING - something unexpected but handled
logger.warning("Stock low", extra={"product_id": product.id, "stock": 5})

# ERROR - operation failed
logger.error("Payment failed", extra={"order_id": order.id})

# CRITICAL - system-level failure
logger.critical("Database connection lost")
```

### 6. Log External Service Calls

```python
from app.core.monitoring import ExternalServiceMonitor

try:
    start = time.time()
    result = razorpay_client.create_order(...)
    duration = time.time() - start
    
    ExternalServiceMonitor.log_external_service_success(
        "razorpay",
        "create_order",
        duration
    )
except Exception as e:
    ExternalServiceMonitor.log_external_service_failure(
        "razorpay",
        "create_order",
        str(e)
    )
```

## Troubleshooting

### Logs Not Appearing in CloudWatch

1. Check ECS task IAM role has CloudWatch Logs permissions
2. Verify log group exists
3. Check log configuration in task definition
4. Look for errors in ECS service events

### High Log Volume

1. Reduce log level in production (INFO instead of DEBUG)
2. Sample high-frequency logs
3. Use log filtering
4. Increase retention period for important logs only

### Missing Context in Logs

1. Ensure middleware adds request_id
2. Check extra fields are being passed
3. Verify JSON formatter is configured
4. Review logging configuration

## Cost Optimization

CloudWatch Logs pricing:

- Ingestion: $0.50 per GB
- Storage: $0.03 per GB per month
- Insights queries: $0.005 per GB scanned

Tips to reduce costs:

1. Set appropriate retention periods (7 days for most logs)
2. Use log sampling for high-volume logs
3. Filter out unnecessary logs
4. Archive old logs to S3 ($0.023 per GB per month)
5. Use log groups efficiently

## Resources

- [CloudWatch Logs Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structured Logging Best Practices](https://www.structlog.org/en/stable/)
