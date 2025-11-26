# Database Backup and Recovery Plan

This document outlines the backup and recovery procedures for IndoStar Naturals.

## Table of Contents

1. [Backup Strategy](#backup-strategy)
2. [Automated Backups](#automated-backups)
3. [Manual Backups](#manual-backups)
4. [Backup Verification](#backup-verification)
5. [Recovery Procedures](#recovery-procedures)
6. [Disaster Recovery](#disaster-recovery)
7. [Testing](#testing)

## Backup Strategy

### Backup Types

**Full Backups**:
- Complete database snapshot
- Frequency: Daily at 2 AM UTC
- Retention: 30 days
- Storage: S3 with versioning

**Incremental Backups**:
- Transaction logs (WAL)
- Frequency: Continuous
- Retention: 7 days
- Storage: S3

**Point-in-Time Recovery**:
- Enabled via WAL archiving
- Recovery window: 7 days
- RPO (Recovery Point Objective): 5 minutes
- RTO (Recovery Time Objective): 1 hour

### Backup Locations

**Primary**: AWS S3 bucket `indostar-backups-primary`
- Region: us-east-1
- Versioning: Enabled
- Encryption: AES-256

**Secondary**: AWS S3 bucket `indostar-backups-secondary`
- Region: us-west-2 (cross-region replication)
- Versioning: Enabled
- Encryption: AES-256

**Tertiary**: Glacier for long-term archival
- Retention: 1 year
- Transition: After 90 days in S3

## Automated Backups

### RDS Automated Backups

RDS provides automated backups with point-in-time recovery.

**Configuration**:
```bash
# Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier indostar-production \
  --backup-retention-period 7 \
  --preferred-backup-window "02:00-03:00" \
  --apply-immediately

# Enable point-in-time recovery
aws rds modify-db-instance \
  --db-instance-identifier indostar-production \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --apply-immediately
```

**Verification**:
```bash
# Check backup status
aws rds describe-db-instances \
  --db-instance-identifier indostar-production \
  --query 'DBInstances[0].{BackupRetention:BackupRetentionPeriod,LatestBackup:LatestRestorableTime}'

# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier indostar-production
```

### Custom Backup Script

For additional control, use a custom backup script:

```bash
#!/bin/bash
# backup-database.sh

set -e

# Configuration
DB_HOST="indostar-production.xxxxx.us-east-1.rds.amazonaws.com"
DB_NAME="indostar_naturals"
DB_USER="indostar_user"
DB_PASSWORD="$DB_PASSWORD"  # From environment
BACKUP_DIR="/backups"
S3_BUCKET="s3://indostar-backups-primary"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="indostar_${DATE}.sql.gz"

# Create backup
echo "Starting backup at $(date)"
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_DIR}/${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    echo "Backup created successfully: ${BACKUP_FILE}"
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    echo "Backup size: ${SIZE}"
else
    echo "ERROR: Backup file not created"
    exit 1
fi

# Upload to S3
echo "Uploading to S3..."
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "${S3_BUCKET}/daily/${BACKUP_FILE}"

# Verify upload
if aws s3 ls "${S3_BUCKET}/daily/${BACKUP_FILE}"; then
    echo "Backup uploaded successfully"
else
    echo "ERROR: Backup upload failed"
    exit 1
fi

# Clean up local backup
rm "${BACKUP_DIR}/${BACKUP_FILE}"

# Delete old backups (keep 30 days)
echo "Cleaning up old backups..."
aws s3 ls "${S3_BUCKET}/daily/" | \
  awk '{print $4}' | \
  head -n -30 | \
  xargs -I {} aws s3 rm "${S3_BUCKET}/daily/{}"

echo "Backup completed at $(date)"

# Send notification
curl -X POST https://api.indostarnaturals.com/api/v1/internal/backup-notification \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"success\",\"backup_file\":\"${BACKUP_FILE}\",\"size\":\"${SIZE}\"}"
```

### Scheduling Backups

**Using Cron**:
```bash
# Add to crontab
0 2 * * * /opt/scripts/backup-database.sh >> /var/log/backup.log 2>&1
```

**Using Kubernetes CronJob**:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: indostar-naturals
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
                --format=custom --compress=9 \
                --file=/tmp/backup.sql.gz
              aws s3 cp /tmp/backup.sql.gz s3://indostar-backups-primary/daily/backup-$(date +%Y%m%d).sql.gz
            env:
            - name: DB_HOST
              valueFrom:
                secretKeyRef:
                  name: indostar-secrets
                  key: DATABASE_HOST
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: indostar-secrets
                  key: DATABASE_USER
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: indostar-secrets
                  key: DATABASE_PASSWORD
          restartPolicy: OnFailure
```

## Manual Backups

### Before Major Changes

Always create a manual backup before:
- Database migrations
- Major deployments
- Schema changes
- Data migrations

**Create Manual Backup**:
```bash
# Using RDS
aws rds create-db-snapshot \
  --db-instance-identifier indostar-production \
  --db-snapshot-identifier indostar-manual-$(date +%Y%m%d-%H%M%S)

# Using pg_dump
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  --format=custom \
  --compress=9 \
  --file=backup-manual-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to S3
aws s3 cp backup-manual-*.sql.gz s3://indostar-backups-primary/manual/
```

### Exporting Specific Data

**Export specific tables**:
```bash
# Export orders table
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --table=orders \
  --format=custom \
  --file=orders-backup.sql.gz

# Export data as CSV
psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
  -c "\copy orders TO 'orders.csv' CSV HEADER"
```

**Export for analysis**:
```bash
# Export last 30 days of orders
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << EOF
\copy (
  SELECT * FROM orders 
  WHERE created_at > NOW() - INTERVAL '30 days'
) TO 'orders-30days.csv' CSV HEADER
EOF
```

## Backup Verification

### Automated Verification

**Verify backup integrity**:
```bash
#!/bin/bash
# verify-backup.sh

BACKUP_FILE=$1

# Test restore to temporary database
echo "Verifying backup: ${BACKUP_FILE}"

# Download from S3
aws s3 cp "s3://indostar-backups-primary/daily/${BACKUP_FILE}" /tmp/

# Create test database
psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE backup_test;"

# Restore backup
pg_restore \
  -h $DB_HOST \
  -U $DB_USER \
  -d backup_test \
  --no-owner \
  --no-acl \
  /tmp/${BACKUP_FILE}

# Verify data
RECORD_COUNT=$(psql -h $DB_HOST -U $DB_USER -d backup_test -t -c "SELECT COUNT(*) FROM orders;")

if [ $RECORD_COUNT -gt 0 ]; then
    echo "Backup verification successful: ${RECORD_COUNT} orders found"
    STATUS="success"
else
    echo "ERROR: Backup verification failed"
    STATUS="failed"
fi

# Clean up
psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE backup_test;"
rm /tmp/${BACKUP_FILE}

# Send notification
curl -X POST https://api.indostarnaturals.com/api/v1/internal/backup-verification \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"${STATUS}\",\"backup_file\":\"${BACKUP_FILE}\",\"record_count\":${RECORD_COUNT}}"
```

### Monthly Verification

Perform full restore test monthly:

1. Create test environment
2. Restore latest backup
3. Run application tests
4. Verify data integrity
5. Document results

## Recovery Procedures

### Scenario 1: Accidental Data Deletion

**If deletion just happened (< 5 minutes)**:

```sql
-- Check if data is in recent backup
-- Connect to database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

-- Start transaction
BEGIN;

-- Restore deleted records from backup
-- (Assuming you have a backup table or can restore to temp database)
INSERT INTO orders 
SELECT * FROM backup_orders 
WHERE id IN (123, 456, 789);

-- Verify
SELECT * FROM orders WHERE id IN (123, 456, 789);

-- Commit if correct
COMMIT;
-- Or rollback if not
ROLLBACK;
```

**If deletion was hours ago**:

1. Identify exact time of deletion
2. Use point-in-time recovery
3. Restore to temporary database
4. Extract deleted data
5. Import to production

### Scenario 2: Database Corruption

**Symptoms**:
- Database won't start
- Corruption errors in logs
- Data inconsistencies

**Recovery**:

```bash
# 1. Stop application
kubectl scale deployment/backend --replicas=0 -n indostar-naturals

# 2. Create snapshot of current state (even if corrupted)
aws rds create-db-snapshot \
  --db-instance-identifier indostar-production \
  --db-snapshot-identifier indostar-corrupted-$(date +%Y%m%d)

# 3. Restore from latest good backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier indostar-production-restored \
  --db-snapshot-identifier <latest-good-snapshot>

# 4. Update application to point to restored database
kubectl set env deployment/backend \
  DATABASE_URL=<new-database-url> \
  -n indostar-naturals

# 5. Start application
kubectl scale deployment/backend --replicas=3 -n indostar-naturals

# 6. Verify application is working
curl https://api.indostarnaturals.com/health

# 7. If successful, delete corrupted database
aws rds delete-db-instance \
  --db-instance-identifier indostar-production \
  --skip-final-snapshot

# 8. Rename restored database
aws rds modify-db-instance \
  --db-instance-identifier indostar-production-restored \
  --new-db-instance-identifier indostar-production \
  --apply-immediately
```

### Scenario 3: Point-in-Time Recovery

**Use case**: Restore database to specific point in time

```bash
# 1. Identify target time
TARGET_TIME="2024-01-15T10:30:00Z"

# 2. Create new instance from point-in-time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier indostar-production \
  --target-db-instance-identifier indostar-pitr-$(date +%Y%m%d) \
  --restore-time $TARGET_TIME

# 3. Wait for restore to complete
aws rds wait db-instance-available \
  --db-instance-identifier indostar-pitr-$(date +%Y%m%d)

# 4. Extract needed data
pg_dump -h <pitr-endpoint> -U $DB_USER -d $DB_NAME \
  --table=orders \
  --data-only \
  --file=recovered-orders.sql

# 5. Import to production
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < recovered-orders.sql

# 6. Verify data
psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
  -c "SELECT COUNT(*) FROM orders WHERE created_at >= '$TARGET_TIME';"

# 7. Delete PITR instance
aws rds delete-db-instance \
  --db-instance-identifier indostar-pitr-$(date +%Y%m%d) \
  --skip-final-snapshot
```

### Scenario 4: Complete Database Loss

**Recovery from S3 backup**:

```bash
# 1. Create new RDS instance
aws rds create-db-instance \
  --db-instance-identifier indostar-production-new \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username indostar_user \
  --master-user-password <password> \
  --allocated-storage 100 \
  --storage-type gp3 \
  --multi-az \
  --backup-retention-period 7

# 2. Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier indostar-production-new

# 3. Download latest backup from S3
LATEST_BACKUP=$(aws s3 ls s3://indostar-backups-primary/daily/ | sort | tail -n 1 | awk '{print $4}')
aws s3 cp "s3://indostar-backups-primary/daily/${LATEST_BACKUP}" /tmp/

# 4. Restore backup
pg_restore \
  -h <new-db-endpoint> \
  -U indostar_user \
  -d indostar_naturals \
  --no-owner \
  --no-acl \
  /tmp/${LATEST_BACKUP}

# 5. Verify restoration
psql -h <new-db-endpoint> -U indostar_user -d indostar_naturals \
  -c "SELECT COUNT(*) FROM orders;"

# 6. Update application
kubectl set env deployment/backend \
  DATABASE_URL=<new-database-url> \
  -n indostar-naturals

# 7. Restart application
kubectl rollout restart deployment/backend -n indostar-naturals
```

## Disaster Recovery

### DR Plan Overview

**RTO (Recovery Time Objective)**: 1 hour
**RPO (Recovery Point Objective)**: 5 minutes

### DR Scenarios

**Scenario 1: Single AZ Failure**
- RDS Multi-AZ automatically fails over
- No action required
- Downtime: < 2 minutes

**Scenario 2: Region Failure**
- Restore from cross-region backup
- Update DNS to point to DR region
- Downtime: < 1 hour

**Scenario 3: Complete AWS Outage**
- Restore to alternative cloud provider
- Use S3 backups stored in Glacier
- Downtime: < 4 hours

### DR Runbook

**Step 1: Assess Situation**
```bash
# Check AWS status
curl https://status.aws.amazon.com/

# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier indostar-production

# Check application health
curl https://api.indostarnaturals.com/health
```

**Step 2: Activate DR**
```bash
# If region failure, restore in DR region
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier indostar-production-dr \
  --db-snapshot-identifier <latest-snapshot> \
  --region us-west-2

# Update Route 53 to point to DR region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dr-dns-change.json
```

**Step 3: Verify DR**
```bash
# Test database connectivity
psql -h <dr-db-endpoint> -U indostar_user -d indostar_naturals -c "SELECT 1;"

# Test application
curl https://api.indostarnaturals.com/health

# Verify data
psql -h <dr-db-endpoint> -U indostar_user -d indostar_naturals \
  -c "SELECT COUNT(*) FROM orders;"
```

**Step 4: Communicate**
- Update status page
- Notify users via email
- Post on social media
- Update support team

**Step 5: Monitor**
- Watch error rates
- Monitor performance
- Check user reports
- Review logs

## Testing

### Monthly DR Test

**Schedule**: First Sunday of each month at 2 AM

**Procedure**:
1. Create test environment
2. Restore latest backup
3. Run application tests
4. Verify data integrity
5. Test failover procedures
6. Document results
7. Update DR plan if needed

**Test Checklist**:
- [ ] Backup restoration successful
- [ ] Database accessible
- [ ] Application starts correctly
- [ ] API endpoints responding
- [ ] Data integrity verified
- [ ] Performance acceptable
- [ ] Failover time within RTO
- [ ] Data loss within RPO

### Quarterly Full DR Drill

**Schedule**: First Sunday of each quarter

**Procedure**:
1. Simulate complete region failure
2. Activate DR procedures
3. Restore in DR region
4. Update DNS
5. Verify application functionality
6. Measure RTO and RPO
7. Document lessons learned
8. Update DR plan

## Backup Monitoring

### Metrics to Monitor

- Backup success rate
- Backup duration
- Backup size
- Restore test success rate
- Time since last successful backup
- S3 storage usage

### Alerts

**Critical Alerts**:
- Backup failed
- Backup not completed in 24 hours
- Restore test failed
- S3 storage > 90% quota

**Warning Alerts**:
- Backup duration > 1 hour
- Backup size increased > 50%
- S3 storage > 80% quota

### Monitoring Script

```bash
#!/bin/bash
# monitor-backups.sh

# Check last backup time
LAST_BACKUP=$(aws s3 ls s3://indostar-backups-primary/daily/ | sort | tail -n 1 | awk '{print $1, $2}')
LAST_BACKUP_EPOCH=$(date -d "$LAST_BACKUP" +%s)
CURRENT_EPOCH=$(date +%s)
HOURS_SINCE_BACKUP=$(( ($CURRENT_EPOCH - $LAST_BACKUP_EPOCH) / 3600 ))

if [ $HOURS_SINCE_BACKUP -gt 24 ]; then
    echo "CRITICAL: Last backup was $HOURS_SINCE_BACKUP hours ago"
    # Send alert
    curl -X POST https://api.indostarnaturals.com/api/v1/internal/alert \
      -H "Content-Type: application/json" \
      -d "{\"severity\":\"critical\",\"message\":\"Backup overdue by $HOURS_SINCE_BACKUP hours\"}"
fi

# Check backup size
LATEST_BACKUP=$(aws s3 ls s3://indostar-backups-primary/daily/ | sort | tail -n 1 | awk '{print $4}')
BACKUP_SIZE=$(aws s3 ls "s3://indostar-backups-primary/daily/${LATEST_BACKUP}" | awk '{print $3}')
BACKUP_SIZE_GB=$(echo "scale=2; $BACKUP_SIZE / 1024 / 1024 / 1024" | bc)

echo "Latest backup: ${LATEST_BACKUP}"
echo "Backup size: ${BACKUP_SIZE_GB} GB"
echo "Hours since backup: ${HOURS_SINCE_BACKUP}"
```

## Best Practices

1. **Test Restores Regularly**: Backups are useless if you can't restore
2. **Automate Everything**: Manual processes are error-prone
3. **Monitor Backups**: Set up alerts for failures
4. **Document Procedures**: Keep runbooks up to date
5. **Encrypt Backups**: Protect sensitive data
6. **Multiple Locations**: Store backups in multiple regions
7. **Retention Policy**: Balance cost and compliance
8. **Version Control**: Keep backup scripts in git
9. **Access Control**: Limit who can delete backups
10. **Audit Trail**: Log all backup and restore operations

## Compliance

### Data Retention

- **Transactional Data**: 7 years
- **User Data**: Until account deletion + 30 days
- **Audit Logs**: 1 year
- **Backups**: 30 days (daily), 1 year (monthly archives)

### Encryption

- All backups encrypted at rest (AES-256)
- All backups encrypted in transit (TLS 1.2+)
- Encryption keys managed via AWS KMS

### Access Control

- Backup access requires MFA
- Restore operations logged and audited
- Principle of least privilege

## Resources

- [AWS RDS Backup Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [AWS S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [Disaster Recovery Best Practices](https://aws.amazon.com/disaster-recovery/)
