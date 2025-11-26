# Infrastructure Setup Guide

This directory contains Terraform configurations for setting up the production infrastructure for IndoStar Naturals on AWS.

## Architecture Overview

The infrastructure includes:

- **VPC**: Multi-AZ VPC with public and private subnets
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **ElastiCache Redis**: Redis cluster for caching and Celery
- **S3 + CloudFront**: Media storage with CDN
- **Application Load Balancer**: HTTPS load balancer with SSL termination
- **ECS Fargate**: Container orchestration (alternative to Kubernetes)
- **Auto Scaling**: Automatic scaling based on CPU/memory
- **Route 53**: DNS management

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (>= 1.0)
3. **AWS CLI** configured with credentials
4. **Domain name** registered and managed in Route 53
5. **ACM Certificate** for HTTPS (must be in us-east-1 for CloudFront)

## Initial Setup

### 1. Create S3 Backend for Terraform State

```bash
# Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket indostar-terraform-state \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket indostar-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket indostar-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name indostar-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Request ACM Certificate

```bash
# Request certificate for your domain
aws acm request-certificate \
  --domain-name indostarnaturals.com \
  --subject-alternative-names "*.indostarnaturals.com" \
  --validation-method DNS \
  --region us-east-1

# Note the CertificateArn from the output
# Validate the certificate by adding DNS records shown in the console
```

### 3. Create terraform.tfvars

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

Example `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "production"

# Database
db_username = "indostar_admin"
db_password = "your-strong-password-here"
db_multi_az = true
db_backup_retention = 7

# Domain and SSL
domain_name = "indostarnaturals.com"
acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/xxxxx"

# Scaling
autoscaling_min_capacity = 3
autoscaling_max_capacity = 10
```

## Deployment

### Initialize Terraform

```bash
terraform init
```

### Plan Infrastructure Changes

```bash
terraform plan -out=tfplan
```

Review the plan carefully before applying.

### Apply Infrastructure

```bash
terraform apply tfplan
```

This will create all the infrastructure resources. The process takes approximately 15-20 minutes.

### Get Outputs

```bash
terraform output
```

Save these outputs - you'll need them for application configuration.

## Post-Deployment Configuration

### 1. Update DNS Records

If your domain is not in Route 53, manually create these DNS records:

```
A     indostarnaturals.com     -> ALB DNS (from terraform output)
CNAME www.indostarnaturals.com -> indostarnaturals.com
CNAME api.indostarnaturals.com -> ALB DNS
CNAME cdn.indostarnaturals.com -> CloudFront DNS (from terraform output)
```

### 2. Run Database Migrations

```bash
# Get RDS endpoint from terraform output
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Run migrations using ECS task
aws ecs run-task \
  --cluster indostar-production \
  --task-definition indostar-backend-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

### 3. Create Initial Owner Account

```bash
# Connect to RDS and run the initial owner creation script
# Or use the backend API endpoint to create the owner account
```

### 4. Configure Application Secrets

Update the ECS task definitions with actual secret values:

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name indostar/production/app-secrets \
  --secret-string file://secrets.json

# Update ECS task definition to reference secrets
```

## Infrastructure Management

### Scaling

#### Manual Scaling

```bash
# Scale backend service
aws ecs update-service \
  --cluster indostar-production \
  --service indostar-backend \
  --desired-count 5
```

#### Auto Scaling

Auto scaling is configured automatically based on:
- CPU utilization > 70%
- Memory utilization > 80%

### Monitoring

View CloudWatch metrics:

```bash
# Backend service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=indostar-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### Backups

RDS automated backups are configured with 7-day retention. To create a manual snapshot:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier indostar-production \
  --db-snapshot-identifier indostar-manual-snapshot-$(date +%Y%m%d)
```

### Disaster Recovery

To restore from backup:

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier indostar-production

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier indostar-production-restored \
  --db-snapshot-identifier snapshot-name
```

## Cost Optimization

### Estimated Monthly Costs (us-east-1)

- RDS db.t3.medium Multi-AZ: ~$120
- ElastiCache cache.t3.medium (2 nodes): ~$100
- ECS Fargate (3 tasks, 1 vCPU, 2GB each): ~$90
- Application Load Balancer: ~$25
- S3 + CloudFront (100GB storage, 1TB transfer): ~$50
- Route 53 (1 hosted zone): ~$0.50
- Data Transfer: ~$50

**Total: ~$435/month** (excluding data transfer overages)

### Cost Reduction Tips

1. Use Reserved Instances for RDS (save up to 60%)
2. Use Savings Plans for ECS Fargate (save up to 50%)
3. Enable S3 Intelligent-Tiering
4. Use CloudFront caching effectively
5. Monitor and optimize data transfer

## Cleanup

To destroy all infrastructure:

```bash
# WARNING: This will delete all resources including databases!
terraform destroy
```

## Troubleshooting

### ECS Tasks Not Starting

Check task logs:
```bash
aws logs tail /ecs/indostar-backend --follow
```

### Database Connection Issues

Verify security groups allow traffic:
```bash
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### SSL Certificate Issues

Verify certificate status:
```bash
aws acm describe-certificate --certificate-arn arn:aws:acm:...
```

## Support

For infrastructure issues, check:
1. CloudWatch Logs
2. ECS Service Events
3. RDS Events
4. CloudTrail for API calls
