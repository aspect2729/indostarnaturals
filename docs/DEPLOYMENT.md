# Deployment Guide

This guide covers deploying IndoStar Naturals to production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [AWS ECS Deployment](#aws-ecs-deployment)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Post-Deployment](#post-deployment)
10. [Rollback Procedures](#rollback-procedures)

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Domain name registered and DNS configured
- [ ] SSL certificate obtained (Let's Encrypt or ACM)
- [ ] PostgreSQL database (RDS or managed service)
- [ ] Redis cluster (ElastiCache or managed service)
- [ ] S3 bucket for media storage
- [ ] CloudFront CDN configured
- [ ] Email service configured (SendGrid/SES)
- [ ] SMS service configured (Twilio/MSG91)
- [ ] Razorpay account with API keys
- [ ] Sentry account for error tracking

### Code Preparation

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Version tagged in git
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] Backup procedures tested

### Security

- [ ] Secrets stored securely (AWS Secrets Manager/Vault)
- [ ] Strong passwords generated
- [ ] JWT secret key generated (min 32 characters)
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Security headers configured

## Environment Setup

### Required Environment Variables

Create a `.env.prod` file with these variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/indostar_naturals
POSTGRES_USER=indostar_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=indostar_naturals

# Redis
REDIS_URL=redis://:password@elasticache-endpoint:6379/0
REDIS_PASSWORD=<strong-password>

# JWT
JWT_SECRET_KEY=<generate-strong-secret-min-32-chars>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=<razorpay-secret>
RAZORPAY_WEBHOOK_SECRET=<webhook-secret>

# SMS (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=<twilio-token>
TWILIO_PHONE_NUMBER=+1234567890

# Email (SendGrid)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@indostarnaturals.com

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=xxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=<google-secret>

# S3 Storage
S3_BUCKET_NAME=indostar-naturals-media-prod
S3_ACCESS_KEY=AKIAXXXXXXXXXXXXXXXX
S3_SECRET_KEY=<s3-secret>
S3_REGION=us-east-1
CDN_BASE_URL=https://d1234567890abc.cloudfront.net

# Application
FRONTEND_URL=https://indostarnaturals.com
BACKEND_URL=https://api.indostarnaturals.com
ENVIRONMENT=production

# Monitoring
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/1234567
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Security
CORS_ORIGINS=https://indostarnaturals.com,https://www.indostarnaturals.com
ALLOWED_HOSTS=api.indostarnaturals.com,indostarnaturals.com
SECURE_SSL_REDIRECT=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Generating Secrets

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate strong password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

## Docker Deployment

### Building Images

```bash
# Build backend image
cd backend
docker build -t indostar-naturals/backend:v1.0.0 -f Dockerfile.prod .

# Build frontend image
cd frontend
docker build -t indostar-naturals/frontend:v1.0.0 -f Dockerfile.prod .

# Tag as latest
docker tag indostar-naturals/backend:v1.0.0 indostar-naturals/backend:latest
docker tag indostar-naturals/frontend:v1.0.0 indostar-naturals/frontend:latest
```

### Pushing to Registry

```bash
# Login to Docker registry
docker login

# Push images
docker push indostar-naturals/backend:v1.0.0
docker push indostar-naturals/backend:latest
docker push indostar-naturals/frontend:v1.0.0
docker push indostar-naturals/frontend:latest
```

### Deploying with Docker Compose

```bash
# Copy production compose file
cp docker-compose.prod.yml /opt/indostar/

# Copy environment file
cp backend/.env.prod /opt/indostar/backend/.env.prod

# Start services
cd /opt/indostar
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Configure kubectl
kubectl config use-context production-cluster
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic indostar-secrets \
  --from-env-file=backend/.env.prod \
  -n indostar-naturals

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/celery-worker-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n indostar-naturals
kubectl get services -n indostar-naturals
kubectl get ingress -n indostar-naturals

# View logs
kubectl logs -f deployment/backend -n indostar-naturals
```

### Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n indostar-naturals

# Scale celery workers
kubectl scale deployment celery-worker --replicas=3 -n indostar-naturals
```

## AWS ECS Deployment

### Using Terraform

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Get outputs
terraform output
```

### Manual ECS Deployment

1. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name indostar-production
```

2. **Create Task Definitions**
```bash
aws ecs register-task-definition --cli-input-json file://ecs-backend-task.json
aws ecs register-task-definition --cli-input-json file://ecs-frontend-task.json
```

3. **Create Services**
```bash
aws ecs create-service \
  --cluster indostar-production \
  --service-name indostar-backend \
  --task-definition indostar-backend:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"
```

## Database Setup

### Running Migrations

```bash
# Using Docker
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Using Kubernetes
kubectl run migration --image=indostar-naturals/backend:latest \
  --restart=Never \
  --env-from=configmap/indostar-config \
  --env-from=secret/indostar-secrets \
  --command -- alembic upgrade head \
  -n indostar-naturals

# Using ECS
aws ecs run-task \
  --cluster indostar-production \
  --task-definition indostar-backend-migration \
  --launch-type FARGATE
```

### Creating Initial Owner

```bash
# Connect to backend container
docker-compose exec backend python

# Or use the init script
docker-compose exec backend python scripts/init_db.py
```

### Database Backup

```bash
# Manual backup
pg_dump -h rds-endpoint -U indostar_user -d indostar_naturals > backup.sql

# Automated backup (RDS)
aws rds create-db-snapshot \
  --db-instance-identifier indostar-production \
  --db-snapshot-identifier indostar-$(date +%Y%m%d-%H%M%S)
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d indostarnaturals.com -d www.indostarnaturals.com -d api.indostarnaturals.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Using AWS ACM

```bash
# Request certificate
aws acm request-certificate \
  --domain-name indostarnaturals.com \
  --subject-alternative-names "*.indostarnaturals.com" \
  --validation-method DNS

# Validate via DNS
# Add CNAME records shown in ACM console to Route 53
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name indostarnaturals.com;

    ssl_certificate /etc/letsencrypt/live/indostarnaturals.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/indostarnaturals.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of configuration
}
```

## Monitoring Setup

### Sentry Configuration

```bash
# Install Sentry CLI
npm install -g @sentry/cli

# Configure
cat > .sentryclirc << EOF
[auth]
token=your-auth-token

[defaults]
org=your-org
project=indostar-naturals
EOF

# Create release
sentry-cli releases new v1.0.0
sentry-cli releases set-commits v1.0.0 --auto
sentry-cli releases finalize v1.0.0
```

### CloudWatch Setup

```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/indostar-backend
aws logs create-log-group --log-group-name /ecs/indostar-celery-worker

# Set retention
aws logs put-retention-policy \
  --log-group-name /ecs/indostar-backend \
  --retention-in-days 7

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name indostar-high-error-rate \
  --alarm-description "Alert on high error rate" \
  --metric-name Errors \
  --namespace IndoStar/Application \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## Post-Deployment

### Verification Checklist

- [ ] Application accessible at domain
- [ ] SSL certificate valid
- [ ] API endpoints responding
- [ ] Database migrations applied
- [ ] Static files loading from CDN
- [ ] Email sending working
- [ ] SMS sending working
- [ ] Payment processing working
- [ ] Webhooks receiving events
- [ ] Monitoring receiving data
- [ ] Logs being collected
- [ ] Backups running

### Smoke Tests

```bash
# Health check
curl https://api.indostarnaturals.com/health

# API test
curl https://api.indostarnaturals.com/api/v1/products

# Frontend test
curl https://indostarnaturals.com

# Check SSL
openssl s_client -connect indostarnaturals.com:443 -servername indostarnaturals.com
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Load test
ab -n 1000 -c 10 https://api.indostarnaturals.com/api/v1/products

# Monitor during test
watch -n 1 'kubectl top pods -n indostar-naturals'
```

## Rollback Procedures

### Docker Rollback

```bash
# Stop current version
docker-compose -f docker-compose.prod.yml down

# Pull previous version
docker pull indostar-naturals/backend:v0.9.0
docker pull indostar-naturals/frontend:v0.9.0

# Update compose file with previous version
# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n indostar-naturals

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n indostar-naturals

# Check rollout status
kubectl rollout status deployment/backend -n indostar-naturals
```

### Database Rollback

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Restore from backup
pg_restore -h rds-endpoint -U indostar_user -d indostar_naturals backup.sql
```

## Troubleshooting

### Application Not Starting

1. Check logs:
```bash
docker-compose logs backend
kubectl logs deployment/backend -n indostar-naturals
```

2. Verify environment variables
3. Check database connectivity
4. Verify Redis connectivity

### Database Connection Issues

1. Check security groups
2. Verify connection string
3. Test connection:
```bash
psql -h rds-endpoint -U indostar_user -d indostar_naturals
```

### SSL Certificate Issues

1. Verify certificate is valid:
```bash
openssl x509 -in cert.pem -text -noout
```

2. Check certificate chain
3. Verify DNS records

### High Memory Usage

1. Check container limits
2. Review application logs for memory leaks
3. Scale horizontally
4. Optimize queries

### Slow Response Times

1. Check database query performance
2. Review Redis cache hit rate
3. Check CDN configuration
4. Enable query logging
5. Use APM tools (Sentry Performance)

## Maintenance

### Regular Tasks

**Daily**:
- Check error logs
- Monitor system health
- Review alerts

**Weekly**:
- Review performance metrics
- Check disk space
- Update dependencies (security patches)

**Monthly**:
- Review and optimize database
- Audit user access
- Test backup restoration
- Review and update documentation

### Updating Application

1. Test in staging
2. Create database backup
3. Tag new version in git
4. Build and push new images
5. Update deployment
6. Run migrations
7. Verify deployment
8. Monitor for issues

## Security Best Practices

1. **Keep Secrets Secure**: Never commit secrets to git
2. **Use Strong Passwords**: Minimum 16 characters
3. **Enable MFA**: For all admin accounts
4. **Regular Updates**: Apply security patches promptly
5. **Monitor Access**: Review audit logs regularly
6. **Limit Permissions**: Principle of least privilege
7. **Encrypt Data**: At rest and in transit
8. **Regular Backups**: Test restoration procedures
9. **Security Scanning**: Use tools like Snyk, Trivy
10. **Incident Response**: Have a plan ready

## Support

For deployment issues:
- Email: devops@indostarnaturals.com
- Slack: #deployments
- On-call: +91-XXXX-XXXXXX

## Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Terraform Documentation](https://www.terraform.io/docs/)
