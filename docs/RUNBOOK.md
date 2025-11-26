# Operations Runbook

This runbook provides step-by-step procedures for handling common operational issues with IndoStar Naturals.

## Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [System Architecture](#system-architecture)
3. [Common Issues](#common-issues)
4. [Incident Response](#incident-response)
5. [Monitoring and Alerts](#monitoring-and-alerts)
6. [Maintenance Procedures](#maintenance-procedures)

## Emergency Contacts

### On-Call Rotation

- **Primary**: +91-XXXX-XXXXXX
- **Secondary**: +91-XXXX-XXXXXX
- **Manager**: +91-XXXX-XXXXXX

### External Services

- **AWS Support**: https://console.aws.amazon.com/support/
- **Razorpay Support**: support@razorpay.com, +91-XXXX-XXXXXX
- **Twilio Support**: https://www.twilio.com/help/contact
- **SendGrid Support**: https://support.sendgrid.com/

### Escalation Path

1. On-call engineer (15 minutes)
2. Secondary on-call (30 minutes)
3. Engineering manager (1 hour)
4. CTO (2 hours)

## System Architecture

### Components

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│  CloudFront CDN             │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│  Application Load Balancer  │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│  Backend API (ECS/K8s)      │
│  - FastAPI                  │
│  - Celery Workers           │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│  Data Layer                 │
│  - PostgreSQL (RDS)         │
│  - Redis (ElastiCache)      │
└─────────────────────────────┘
```

### Key URLs

- **Production**: https://indostarnaturals.com
- **API**: https://api.indostarnaturals.com
- **Admin**: https://indostarnaturals.com/admin
- **Status Page**: https://status.indostarnaturals.com
- **Monitoring**: https://sentry.io/organizations/indostar/
- **Logs**: CloudWatch Logs

## Common Issues

### Issue 1: Application Down / 502 Bad Gateway

**Symptoms**:
- Users cannot access the website
- 502 Bad Gateway error
- Health check failing

**Diagnosis**:
```bash
# Check backend pods/containers
kubectl get pods -n indostar-naturals
# or
docker-compose ps

# Check logs
kubectl logs deployment/backend -n indostar-naturals --tail=100
# or
docker-compose logs backend --tail=100

# Check health endpoint
curl https://api.indostarnaturals.com/health
```

**Common Causes**:
1. Backend containers crashed
2. Database connection lost
3. Out of memory
4. Deployment in progress

**Resolution**:

**If containers crashed**:
```bash
# Kubernetes
kubectl rollout restart deployment/backend -n indostar-naturals

# Docker
docker-compose restart backend
```

**If database connection lost**:
```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier indostar-production

# Test connection
psql -h <rds-endpoint> -U indostar_user -d indostar_naturals

# If database is down, check RDS console for issues
# May need to reboot RDS instance
```

**If out of memory**:
```bash
# Check memory usage
kubectl top pods -n indostar-naturals

# Scale up resources
kubectl set resources deployment/backend \
  --limits=memory=4Gi \
  -n indostar-naturals

# Or scale horizontally
kubectl scale deployment/backend --replicas=5 -n indostar-naturals
```

**Prevention**:
- Set up proper health checks
- Configure auto-scaling
- Monitor memory usage
- Set resource limits

---

### Issue 2: Slow Response Times

**Symptoms**:
- Pages loading slowly
- API timeouts
- Users complaining about performance

**Diagnosis**:
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.indostarnaturals.com/api/v1/products

# Check database performance
# In psql:
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

# Check Redis
redis-cli --latency

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 300 \
  --statistics Average
```

**Common Causes**:
1. Slow database queries
2. Redis cache miss
3. High CPU usage
4. Network issues
5. Unoptimized code

**Resolution**:

**For slow queries**:
```sql
-- Add missing indexes
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- Analyze tables
ANALYZE products;
ANALYZE orders;
```

**For cache issues**:
```bash
# Check Redis memory
redis-cli INFO memory

# Clear cache if needed (use carefully!)
redis-cli FLUSHDB

# Increase cache TTL in code
```

**For high CPU**:
```bash
# Scale horizontally
kubectl scale deployment/backend --replicas=5 -n indostar-naturals

# Or vertically
kubectl set resources deployment/backend \
  --limits=cpu=2000m \
  -n indostar-naturals
```

**Prevention**:
- Regular query optimization
- Proper indexing
- Cache warming
- Load testing
- Performance monitoring

---

### Issue 3: Payment Processing Failures

**Symptoms**:
- Orders stuck in pending
- Payment webhook not received
- Users reporting payment issues

**Diagnosis**:
```bash
# Check webhook logs
kubectl logs deployment/backend -n indostar-naturals | grep webhook

# Check Razorpay dashboard
# Go to https://dashboard.razorpay.com/app/webhooks

# Check payment records
# In database:
SELECT * FROM payments 
WHERE status = 'pending' 
AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

# Check Sentry for errors
# Filter by "payment" or "razorpay"
```

**Common Causes**:
1. Webhook signature verification failing
2. Razorpay service down
3. Network timeout
4. Invalid API keys
5. Webhook URL not configured

**Resolution**:

**If webhook not received**:
```bash
# Verify webhook URL in Razorpay dashboard
# Should be: https://api.indostarnaturals.com/api/v1/webhooks/razorpay

# Check webhook secret matches
echo $RAZORPAY_WEBHOOK_SECRET

# Manually trigger webhook from Razorpay dashboard
```

**If signature verification failing**:
```python
# Verify webhook secret is correct
# Check backend logs for signature mismatch errors

# Update webhook secret if needed
kubectl set env deployment/backend \
  RAZORPAY_WEBHOOK_SECRET=<new-secret> \
  -n indostar-naturals
```

**If Razorpay down**:
```bash
# Check Razorpay status
curl https://status.razorpay.com/

# If down, wait for resolution
# Communicate with users about delay
```

**Manual payment reconciliation**:
```python
# Connect to backend
kubectl exec -it deployment/backend -n indostar-naturals -- python

# Run reconciliation script
from app.services.payment_service import PaymentService
from app.core.database import SessionLocal

db = SessionLocal()
payment_service = PaymentService()

# Get pending payments
pending_payments = db.query(Payment).filter(
    Payment.status == 'pending',
    Payment.created_at > datetime.now() - timedelta(hours=24)
).all()

# Check each with Razorpay
for payment in pending_payments:
    razorpay_payment = razorpay_client.payment.fetch(payment.razorpay_payment_id)
    if razorpay_payment['status'] == 'captured':
        payment_service.handle_payment_success(payment.razorpay_payment_id, payment.order_id)
```

**Prevention**:
- Monitor webhook delivery
- Set up alerts for payment failures
- Regular reconciliation
- Test webhook in staging

---

### Issue 4: High Error Rate

**Symptoms**:
- Sentry showing many errors
- CloudWatch alarms firing
- Users reporting errors

**Diagnosis**:
```bash
# Check Sentry dashboard
# Look for error patterns

# Check logs
kubectl logs deployment/backend -n indostar-naturals | grep ERROR

# Check error rate
aws cloudwatch get-metric-statistics \
  --namespace IndoStar/Application \
  --metric-name Errors \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 300 \
  --statistics Sum
```

**Common Causes**:
1. Recent deployment introduced bug
2. External service down
3. Database issues
4. Configuration error

**Resolution**:

**If recent deployment**:
```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n indostar-naturals

# Verify rollback
kubectl rollout status deployment/backend -n indostar-naturals

# Check error rate after rollback
```

**If external service down**:
```bash
# Check service status
curl https://status.twilio.com/
curl https://status.sendgrid.com/

# Implement circuit breaker if not already
# Disable non-critical features temporarily
```

**If database issues**:
```bash
# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

# Kill long-running queries if needed
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
AND query_start < NOW() - INTERVAL '5 minutes';
```

**Prevention**:
- Thorough testing before deployment
- Gradual rollouts
- Feature flags
- Circuit breakers
- Proper error handling

---

### Issue 5: Database Connection Pool Exhausted

**Symptoms**:
- "Too many connections" errors
- Application hanging
- Timeouts

**Diagnosis**:
```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check connection limit
SHOW max_connections;

# Check connections by state
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;

# Check application pool settings
# In backend logs, look for pool exhaustion warnings
```

**Common Causes**:
1. Connection leaks
2. Pool size too small
3. Long-running queries
4. Too many application instances

**Resolution**:

**Immediate**:
```bash
# Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < NOW() - INTERVAL '10 minutes';

# Restart application to reset pools
kubectl rollout restart deployment/backend -n indostar-naturals
```

**Long-term**:
```python
# Increase pool size in backend config
# In app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase from 10
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)
```

**Prevention**:
- Proper connection management
- Use connection pooling
- Set appropriate timeouts
- Monitor connection usage

---

### Issue 6: Celery Workers Not Processing Tasks

**Symptoms**:
- Emails not sending
- Subscriptions not processing
- Background tasks piling up

**Diagnosis**:
```bash
# Check worker status
kubectl get pods -n indostar-naturals | grep celery

# Check worker logs
kubectl logs deployment/celery-worker -n indostar-naturals

# Check Redis queue
redis-cli LLEN celery

# Check for failed tasks
redis-cli LLEN celery:failed
```

**Common Causes**:
1. Workers crashed
2. Redis connection lost
3. Task errors
4. Memory issues

**Resolution**:

**If workers crashed**:
```bash
# Restart workers
kubectl rollout restart deployment/celery-worker -n indostar-naturals

# Scale up if needed
kubectl scale deployment/celery-worker --replicas=3 -n indostar-naturals
```

**If Redis connection lost**:
```bash
# Check Redis status
redis-cli PING

# Restart Redis if needed (use carefully!)
kubectl rollout restart deployment/redis -n indostar-naturals
```

**If tasks failing**:
```bash
# Check failed tasks
redis-cli LRANGE celery:failed 0 -1

# Retry failed tasks
celery -A app.core.celery_app purge

# Or manually retry specific tasks
```

**Prevention**:
- Monitor worker health
- Set up task retries
- Proper error handling
- Resource limits

---

### Issue 7: Out of Disk Space

**Symptoms**:
- Application crashes
- Cannot write logs
- Database errors

**Diagnosis**:
```bash
# Check disk usage
df -h

# Find large files
du -sh /* | sort -h

# Check log sizes
du -sh /var/log/*

# Check Docker volumes
docker system df
```

**Common Causes**:
1. Log files growing
2. Database growing
3. Docker images accumulating
4. Temp files not cleaned

**Resolution**:

**Immediate**:
```bash
# Clean Docker
docker system prune -a --volumes

# Clean logs
find /var/log -name "*.log" -mtime +7 -delete

# Clean temp files
rm -rf /tmp/*
```

**Long-term**:
```bash
# Set up log rotation
cat > /etc/logrotate.d/indostar << EOF
/var/log/indostar/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF

# Increase disk size
aws ec2 modify-volume --volume-id vol-xxx --size 100

# Set up CloudWatch Logs
# Logs are automatically rotated
```

**Prevention**:
- Log rotation
- Regular cleanup
- Monitor disk usage
- Set up alerts

---

## Incident Response

### Severity Levels

**P0 - Critical**:
- Complete outage
- Data loss
- Security breach
- Response time: Immediate

**P1 - High**:
- Major feature broken
- Significant performance degradation
- Response time: 15 minutes

**P2 - Medium**:
- Minor feature broken
- Workaround available
- Response time: 1 hour

**P3 - Low**:
- Cosmetic issues
- Enhancement requests
- Response time: Next business day

### Incident Response Process

1. **Acknowledge**
   - Acknowledge alert within 5 minutes
   - Update status page
   - Notify team in Slack

2. **Assess**
   - Determine severity
   - Identify affected users
   - Estimate impact

3. **Mitigate**
   - Implement immediate fix or workaround
   - Communicate with users
   - Update status page

4. **Resolve**
   - Implement permanent fix
   - Verify resolution
   - Update status page

5. **Post-Mortem**
   - Document incident
   - Identify root cause
   - Create action items
   - Share learnings

### Communication Templates

**Initial Update**:
```
We're investigating reports of [issue]. We'll provide an update within 30 minutes.
Status: Investigating
```

**Progress Update**:
```
We've identified the issue as [cause]. We're working on a fix. ETA: [time]
Status: Identified
```

**Resolution**:
```
The issue has been resolved. All systems are operating normally. 
We apologize for the inconvenience.
Status: Resolved
```

## Monitoring and Alerts

### Key Metrics to Monitor

**Application**:
- Response time (p50, p95, p99)
- Error rate
- Request rate
- Active users

**Infrastructure**:
- CPU usage
- Memory usage
- Disk usage
- Network I/O

**Business**:
- Orders per hour
- Revenue per hour
- Payment success rate
- Subscription churn rate

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Response Time | > 1s | > 2s |
| Error Rate | > 1% | > 5% |
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 80% | > 95% |
| Disk Usage | > 80% | > 90% |
| Payment Failures | > 5/hour | > 10/hour |

### Checking Alerts

```bash
# CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM

# Sentry issues
# Check https://sentry.io/organizations/indostar/issues/

# Check status page
curl https://status.indostarnaturals.com/api/v1/status
```

## Maintenance Procedures

### Planned Maintenance

1. **Schedule**
   - Choose low-traffic time (2-4 AM IST)
   - Notify users 24 hours in advance
   - Update status page

2. **Backup**
   - Create database snapshot
   - Backup configuration
   - Document current state

3. **Execute**
   - Put application in maintenance mode
   - Perform maintenance
   - Test thoroughly

4. **Restore**
   - Remove maintenance mode
   - Monitor for issues
   - Update status page

### Database Maintenance

```bash
# Vacuum database
VACUUM ANALYZE;

# Reindex
REINDEX DATABASE indostar_naturals;

# Update statistics
ANALYZE;

# Check for bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### Certificate Renewal

```bash
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/indostarnaturals.com/cert.pem -noout -dates

# Renew certificate
certbot renew

# Reload nginx
nginx -s reload
```

## Useful Commands

### Kubernetes

```bash
# Get pod status
kubectl get pods -n indostar-naturals

# Describe pod
kubectl describe pod <pod-name> -n indostar-naturals

# Get logs
kubectl logs <pod-name> -n indostar-naturals

# Execute command in pod
kubectl exec -it <pod-name> -n indostar-naturals -- /bin/bash

# Port forward
kubectl port-forward <pod-name> 8000:8000 -n indostar-naturals

# Scale deployment
kubectl scale deployment/backend --replicas=5 -n indostar-naturals

# Rollback deployment
kubectl rollout undo deployment/backend -n indostar-naturals
```

### Docker

```bash
# List containers
docker ps

# View logs
docker logs <container-id>

# Execute command
docker exec -it <container-id> /bin/bash

# Restart container
docker restart <container-id>

# View resource usage
docker stats
```

### Database

```bash
# Connect to database
psql -h <host> -U <user> -d <database>

# List databases
\l

# List tables
\dt

# Describe table
\d <table-name>

# Run query
SELECT * FROM orders LIMIT 10;

# Export data
\copy (SELECT * FROM orders) TO 'orders.csv' CSV HEADER;
```

### Redis

```bash
# Connect to Redis
redis-cli

# Check memory
INFO memory

# List keys
KEYS *

# Get value
GET key

# Delete key
DEL key

# Flush database (use carefully!)
FLUSHDB
```

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
