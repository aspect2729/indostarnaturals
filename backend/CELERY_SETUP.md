# Celery Background Tasks Setup

This document describes the Celery background task setup for IndoStar Naturals.

## Overview

The application uses Celery for asynchronous task processing with Redis as the message broker and result backend. Tasks are organized into three queues:

1. **default** - General tasks and cleanup operations
2. **notifications** - Email and SMS notifications
3. **subscriptions** - Subscription processing and renewal

## Task Categories

### Notification Tasks (`app.tasks.notifications`)

Handles asynchronous email and SMS sending with automatic retry logic:

- `send_email_task` - Send individual emails
- `send_sms_task` - Send individual SMS messages
- `send_templated_email_task` - Send emails using predefined templates
- `send_templated_sms_task` - Send SMS using predefined templates
- `send_order_confirmation_task` - Send order confirmation via email and SMS
- `send_order_shipped_task` - Send order shipped notification
- `send_payment_failed_task` - Send payment failure notification
- `send_subscription_renewal_reminder_task` - Send subscription renewal reminder

**Retry Policy:**
- Max retries: 3
- Exponential backoff with jitter
- Max backoff: 10 minutes

### Subscription Tasks (`app.tasks.subscriptions`)

Handles subscription processing and recurring deliveries:

- `process_due_subscriptions` - Process all subscriptions due today (scheduled daily at midnight UTC)
- `process_single_subscription` - Process a single subscription delivery
- `send_subscription_renewal_reminders` - Send renewal reminders 24 hours before charge

**Scheduled Tasks:**
- `process_due_subscriptions` runs daily at 00:00 UTC

### Cleanup Tasks (`app.tasks.cleanup`)

Handles periodic cleanup operations:

- `cleanup_expired_carts` - Remove carts not updated in 30 days (scheduled daily at 02:00 UTC)
- `cleanup_expired_tokens` - Clean up expired tokens from Redis (scheduled daily at 03:00 UTC)
- `cleanup_old_audit_logs` - Remove audit logs older than 90 days (optional, not scheduled by default)
- `cleanup_abandoned_sessions` - Clean up abandoned user sessions (optional, not scheduled by default)

**Scheduled Tasks:**
- `cleanup_expired_carts` runs daily at 02:00 UTC
- `cleanup_expired_tokens` runs daily at 03:00 UTC

## Running Celery Workers

### Development

Start a Celery worker for all queues:

```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

Start workers for specific queues:

```bash
# Notifications queue only
celery -A app.core.celery_app worker -Q notifications --loglevel=info

# Subscriptions queue only
celery -A app.core.celery_app worker -Q subscriptions --loglevel=info

# Default queue only
celery -A app.core.celery_app worker -Q default --loglevel=info
```

### Production

Run multiple workers with concurrency:

```bash
# Worker for notifications (4 concurrent tasks)
celery -A app.core.celery_app worker -Q notifications --concurrency=4 --loglevel=info

# Worker for subscriptions (2 concurrent tasks)
celery -A app.core.celery_app worker -Q subscriptions --concurrency=2 --loglevel=info

# Worker for default queue (2 concurrent tasks)
celery -A app.core.celery_app worker -Q default --concurrency=2 --loglevel=info
```

## Running Celery Beat (Scheduler)

Celery Beat is required to run scheduled tasks (subscriptions, cleanup).

### Development

```bash
cd backend
celery -A app.core.celery_app beat --loglevel=info
```

### Production

Use a persistent scheduler:

```bash
celery -A app.core.celery_app beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Or use the default file-based scheduler:

```bash
celery -A app.core.celery_app beat --loglevel=info
```

## Running Both Worker and Beat

For development, you can run both in one process:

```bash
celery -A app.core.celery_app worker --beat --loglevel=info
```

**Note:** In production, run Beat and Workers as separate processes for better reliability.

## Docker Setup

The `docker-compose.yml` includes services for Celery:

```yaml
services:
  worker:
    build: ./backend
    command: celery -A app.core.celery_app worker --loglevel=info
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      # ... other environment variables

  beat:
    build: ./backend
    command: celery -A app.core.celery_app beat --loglevel=info
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      # ... other environment variables
```

Start all services:

```bash
docker-compose up -d
```

## Monitoring Tasks

### Flower (Celery Monitoring Tool)

Install Flower:

```bash
pip install flower
```

Run Flower:

```bash
celery -A app.core.celery_app flower --port=5555
```

Access the web interface at `http://localhost:5555`

### Celery Events

Monitor task events in real-time:

```bash
celery -A app.core.celery_app events
```

### Task Status

Check task status programmatically:

```python
from app.tasks.notifications import send_email_task

# Queue a task
result = send_email_task.delay(
    to_email="user@example.com",
    subject="Test",
    body="Test message"
)

# Check status
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY

# Get result (blocks until task completes)
print(result.get(timeout=10))
```

## Configuration

Celery configuration is in `backend/app/core/celery_app.py`:

- **Broker:** Redis (configured via `REDIS_URL` environment variable)
- **Result Backend:** Redis
- **Task Serializer:** JSON
- **Result Serializer:** JSON
- **Timezone:** UTC
- **Task Time Limit:** 30 minutes
- **Task Soft Time Limit:** 25 minutes
- **Worker Prefetch Multiplier:** 4
- **Worker Max Tasks Per Child:** 1000

## Troubleshooting

### Tasks Not Running

1. Check Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check worker is running:
   ```bash
   celery -A app.core.celery_app inspect active
   ```

3. Check task is registered:
   ```bash
   celery -A app.core.celery_app inspect registered
   ```

### Tasks Failing

1. Check worker logs for errors
2. Check task retry count and backoff
3. Verify external service credentials (Razorpay, SendGrid, Twilio)
4. Check database connectivity

### Scheduled Tasks Not Running

1. Verify Celery Beat is running
2. Check Beat schedule:
   ```bash
   celery -A app.core.celery_app inspect scheduled
   ```

3. Check Beat logs for errors

## Best Practices

1. **Always use `.delay()` or `.apply_async()` to queue tasks** - Never call task functions directly
2. **Keep tasks idempotent** - Tasks should be safe to retry
3. **Use task retries** - Let Celery handle transient failures
4. **Monitor task queues** - Use Flower or similar tools
5. **Set appropriate timeouts** - Prevent tasks from running indefinitely
6. **Use separate queues** - Isolate critical tasks from non-critical ones
7. **Scale workers independently** - Run more workers for high-volume queues

## Environment Variables

Required environment variables for Celery tasks:

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Email Provider (SendGrid or SES)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@indostarnaturals.com

# SMS Provider (Twilio or MSG91)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Application URLs
FRONTEND_URL=https://indostarnaturals.com
BACKEND_URL=https://api.indostarnaturals.com
```

## Testing Tasks

Test tasks in development:

```python
from app.tasks.notifications import send_email_task

# Test email task
result = send_email_task.delay(
    to_email="test@example.com",
    subject="Test Email",
    body="This is a test email"
)

print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")
```

Test scheduled tasks manually:

```python
from app.tasks.subscriptions import process_due_subscriptions
from app.tasks.cleanup import cleanup_expired_carts

# Run subscription processing
process_due_subscriptions.delay()

# Run cart cleanup
cleanup_expired_carts.delay(days_old=30)
```
