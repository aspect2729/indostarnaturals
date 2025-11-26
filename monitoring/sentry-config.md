# Sentry Configuration Guide

This guide explains how to set up Sentry for error tracking and performance monitoring.

## Setup Steps

### 1. Create Sentry Account and Project

1. Go to [sentry.io](https://sentry.io) and create an account
2. Create a new project for "Python" (backend)
3. Create another project for "React" (frontend)
4. Note the DSN (Data Source Name) for each project

### 2. Configure Backend Sentry

The backend is already configured to use Sentry. Update your environment variables:

```bash
# In backend/.env.prod
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/1234567
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of transactions for performance monitoring
```

### 3. Configure Frontend Sentry

Add Sentry to the frontend:

```bash
cd frontend
npm install @sentry/react @sentry/tracing
```

Update `frontend/src/main.tsx`:

```typescript
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_ENVIRONMENT || "production",
    integrations: [new BrowserTracing()],
    tracesSampleRate: 0.1,
    beforeSend(event, hint) {
      // Filter out sensitive data
      if (event.request) {
        delete event.request.cookies;
      }
      return event;
    },
  });
}
```

Add to `frontend/.env.prod`:

```bash
VITE_SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/7654321
VITE_ENVIRONMENT=production
```

### 4. Configure Alerts

In Sentry dashboard:

1. Go to **Alerts** → **Create Alert Rule**
2. Create alerts for:
   - High error rate (> 10 errors/minute)
   - New error types
   - Performance degradation (p95 > 2 seconds)
   - External service failures

### 5. Set Up Integrations

#### Slack Integration

1. Go to **Settings** → **Integrations** → **Slack**
2. Connect your Slack workspace
3. Configure alert notifications to go to #alerts channel

#### GitHub Integration

1. Go to **Settings** → **Integrations** → **GitHub**
2. Connect your GitHub repository
3. Enable automatic issue creation for new errors

### 6. Configure Release Tracking

Add release tracking to deployment scripts:

```bash
# In deploy.sh
if [ "$ENVIRONMENT" = "production" ]; then
    # Create Sentry release
    sentry-cli releases new "$VERSION"
    sentry-cli releases set-commits "$VERSION" --auto
    sentry-cli releases finalize "$VERSION"
    sentry-cli releases deploys "$VERSION" new -e production
fi
```

Install sentry-cli:

```bash
npm install -g @sentry/cli
# or
curl -sL https://sentry.io/get-cli/ | bash
```

Configure sentry-cli:

```bash
# Create .sentryclirc
[auth]
token=your-auth-token

[defaults]
org=your-org-slug
project=indostar-naturals-backend
```

### 7. Custom Context and Tags

The backend already includes custom context. You can add more in your code:

```python
import sentry_sdk

# Add custom context
sentry_sdk.set_context("order", {
    "order_id": order.id,
    "total_amount": float(order.final_amount),
    "user_role": user.role.value
})

# Add custom tags
sentry_sdk.set_tag("payment_provider", "razorpay")
sentry_sdk.set_tag("user_role", user.role.value)

# Add breadcrumbs
sentry_sdk.add_breadcrumb(
    category="order",
    message="Order created",
    level="info",
    data={"order_id": order.id}
)
```

### 8. Performance Monitoring

Enable performance monitoring for critical operations:

```python
import sentry_sdk

# Transaction for order creation
with sentry_sdk.start_transaction(op="order", name="create_order"):
    # Create order
    with sentry_sdk.start_span(op="db", description="Insert order"):
        order = create_order_in_db()
    
    with sentry_sdk.start_span(op="http", description="Create Razorpay order"):
        razorpay_order = create_razorpay_order()
    
    with sentry_sdk.start_span(op="db", description="Update stock"):
        update_product_stock()
```

### 9. Error Filtering

Configure error filtering to reduce noise:

```python
# In backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    integrations=[FastApiIntegration()],
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    before_send=filter_errors,
)

def filter_errors(event, hint):
    # Ignore 404 errors
    if event.get("exception"):
        exc_type = event["exception"]["values"][0]["type"]
        if exc_type == "HTTPException" and hint.get("exc_info"):
            if hint["exc_info"][1].status_code == 404:
                return None
    
    # Filter out sensitive data
    if event.get("request"):
        if "headers" in event["request"]:
            # Remove authorization headers
            event["request"]["headers"].pop("Authorization", None)
            event["request"]["headers"].pop("Cookie", None)
    
    return event
```

### 10. Monitoring Checklist

- [ ] Backend Sentry DSN configured
- [ ] Frontend Sentry DSN configured
- [ ] Alert rules created
- [ ] Slack integration configured
- [ ] GitHub integration configured
- [ ] Release tracking configured
- [ ] Custom tags and context added
- [ ] Performance monitoring enabled
- [ ] Error filtering configured
- [ ] Team members invited to Sentry project

## Best Practices

1. **Use Structured Logging**: Always include context in error logs
2. **Set Appropriate Sample Rates**: Don't sample 100% in production (expensive)
3. **Filter Sensitive Data**: Never send passwords, tokens, or PII to Sentry
4. **Use Releases**: Track which version caused errors
5. **Set Up Alerts**: Get notified immediately for critical errors
6. **Review Regularly**: Check Sentry dashboard weekly for trends
7. **Resolve Issues**: Mark issues as resolved when fixed
8. **Use Breadcrumbs**: Add breadcrumbs for better debugging context

## Troubleshooting

### Sentry Not Receiving Events

1. Check DSN is correct
2. Verify network connectivity
3. Check Sentry SDK is initialized before errors occur
4. Look for initialization errors in logs

### Too Many Events

1. Increase sample rate filtering
2. Add more error filtering
3. Fix recurring errors
4. Use rate limiting in Sentry project settings

### Missing Context

1. Ensure custom context is set before errors
2. Check breadcrumbs are being added
3. Verify tags are set correctly
4. Review before_send filter isn't removing too much

## Cost Optimization

Sentry pricing is based on events and transactions:

1. **Use Sampling**: Sample 10-20% of transactions
2. **Filter Errors**: Don't send 404s and other expected errors
3. **Set Quotas**: Configure monthly quotas in Sentry
4. **Archive Old Issues**: Archive resolved issues after 30 days
5. **Use Spike Protection**: Enable spike protection to avoid overages

## Resources

- [Sentry Python SDK Docs](https://docs.sentry.io/platforms/python/)
- [Sentry React SDK Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Alert Rules](https://docs.sentry.io/product/alerts/)
