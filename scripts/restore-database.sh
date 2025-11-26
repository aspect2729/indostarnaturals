#!/bin/bash
# Database Restore Script for IndoStar Naturals
# This script restores a PostgreSQL database from a backup file

set -e

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-indostar_naturals}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_FILE="$1"
S3_BUCKET="${S3_BUCKET:-s3://indostar-backups-primary}"
TEMP_DIR="/tmp/restore"
LOG_FILE="/var/log/restore.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Show usage
usage() {
    echo "Usage: $0 <backup-file>"
    echo ""
    echo "Examples:"
    echo "  $0 indostar_20240115_020000.sql.gz"
    echo "  $0 s3://indostar-backups-primary/daily/indostar_20240115_020000.sql.gz"
    echo ""
    echo "Environment variables:"
    echo "  DB_HOST      - Database host (default: localhost)"
    echo "  DB_NAME      - Database name (default: indostar_naturals)"
    echo "  DB_USER      - Database user (default: postgres)"
    echo "  DB_PASSWORD  - Database password (required)"
    echo "  S3_BUCKET    - S3 bucket for backups (default: s3://indostar-backups-primary)"
    exit 1
}

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    log_error "No backup file specified"
    usage
fi

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if pg_restore is installed
    if ! command -v pg_restore &> /dev/null; then
        log_error "pg_restore not found. Please install PostgreSQL client."
        exit 1
    fi
    
    # Check if psql is installed
    if ! command -v psql &> /dev/null; then
        log_error "psql not found. Please install PostgreSQL client."
        exit 1
    fi
    
    # Check if DB_PASSWORD is set
    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD environment variable is not set."
        exit 1
    fi
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    log_success "Prerequisites check passed"
}

# Download backup from S3 if needed
download_backup() {
    if [[ "$BACKUP_FILE" == s3://* ]]; then
        log "Downloading backup from S3..."
        LOCAL_FILE="$TEMP_DIR/$(basename $BACKUP_FILE)"
        
        aws s3 cp "$BACKUP_FILE" "$LOCAL_FILE" 2>&1 | tee -a "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            log_success "Backup downloaded from S3"
            BACKUP_FILE="$LOCAL_FILE"
        else
            log_error "Failed to download backup from S3"
            exit 1
        fi
    elif [ ! -f "$BACKUP_FILE" ]; then
        # Try to find in S3
        log "Backup file not found locally, searching in S3..."
        S3_PATH="${S3_BUCKET}/daily/${BACKUP_FILE}"
        LOCAL_FILE="$TEMP_DIR/${BACKUP_FILE}"
        
        aws s3 cp "$S3_PATH" "$LOCAL_FILE" 2>&1 | tee -a "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            log_success "Backup downloaded from S3"
            BACKUP_FILE="$LOCAL_FILE"
        else
            log_error "Backup file not found: $BACKUP_FILE"
            exit 1
        fi
    fi
    
    log "Using backup file: $BACKUP_FILE"
}

# Verify backup file
verify_backup() {
    log "Verifying backup file..."
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup size: $SIZE"
    
    # Verify backup integrity
    if PGPASSWORD=$DB_PASSWORD pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1; then
        log_success "Backup file is valid"
    else
        log_error "Backup file is corrupted or invalid"
        exit 1
    fi
}

# Create backup of current database
backup_current_database() {
    log_warning "Creating backup of current database before restore..."
    
    SAFETY_BACKUP="$TEMP_DIR/safety_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --file="$SAFETY_BACKUP" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Safety backup created: $SAFETY_BACKUP"
        
        # Upload to S3
        aws s3 cp "$SAFETY_BACKUP" "${S3_BUCKET}/safety/$(basename $SAFETY_BACKUP)"
        log "Safety backup uploaded to S3"
    else
        log_error "Failed to create safety backup"
        read -p "Continue without safety backup? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            exit 1
        fi
    fi
}

# Confirm restore
confirm_restore() {
    log_warning "========================================="
    log_warning "WARNING: This will restore the database"
    log_warning "Database: $DB_NAME"
    log_warning "Host: $DB_HOST"
    log_warning "Backup: $BACKUP_FILE"
    log_warning "========================================="
    
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

# Stop application
stop_application() {
    log "Stopping application..."
    
    # If using Kubernetes
    if command -v kubectl &> /dev/null; then
        kubectl scale deployment/backend --replicas=0 -n indostar-naturals 2>&1 | tee -a "$LOG_FILE" || true
        kubectl scale deployment/celery-worker --replicas=0 -n indostar-naturals 2>&1 | tee -a "$LOG_FILE" || true
        log "Application stopped (Kubernetes)"
    fi
    
    # If using Docker Compose
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        docker-compose stop backend celery_worker 2>&1 | tee -a "$LOG_FILE" || true
        log "Application stopped (Docker Compose)"
    fi
    
    # Wait for connections to close
    log "Waiting for database connections to close..."
    sleep 5
}

# Terminate active connections
terminate_connections() {
    log "Terminating active database connections..."
    
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d postgres << EOF
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = '$DB_NAME' 
AND pid <> pg_backend_pid();
EOF
    
    log "Active connections terminated"
}

# Restore database
restore_database() {
    log "Starting database restore..."
    
    # Drop and recreate database
    log "Dropping existing database..."
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d postgres << EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF
    
    if [ $? -eq 0 ]; then
        log_success "Database recreated"
    else
        log_error "Failed to recreate database"
        exit 1
    fi
    
    # Restore from backup
    log "Restoring from backup..."
    PGPASSWORD=$DB_PASSWORD pg_restore \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-owner \
        --no-acl \
        --verbose \
        "$BACKUP_FILE" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Database restored successfully"
    else
        log_error "Database restore failed"
        exit 1
    fi
}

# Verify restore
verify_restore() {
    log "Verifying restore..."
    
    # Check if database exists
    DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
    
    if [ "$DB_EXISTS" != "1" ]; then
        log_error "Database does not exist after restore"
        exit 1
    fi
    
    # Check table count
    TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
    log "Tables restored: $TABLE_COUNT"
    
    if [ "$TABLE_COUNT" -eq 0 ]; then
        log_error "No tables found after restore"
        exit 1
    fi
    
    # Check record counts
    log "Checking record counts..."
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" << EOF
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM subscriptions;
EOF
    
    log_success "Restore verification completed"
}

# Start application
start_application() {
    log "Starting application..."
    
    # If using Kubernetes
    if command -v kubectl &> /dev/null; then
        kubectl scale deployment/backend --replicas=3 -n indostar-naturals 2>&1 | tee -a "$LOG_FILE" || true
        kubectl scale deployment/celery-worker --replicas=2 -n indostar-naturals 2>&1 | tee -a "$LOG_FILE" || true
        log "Application started (Kubernetes)"
    fi
    
    # If using Docker Compose
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        docker-compose start backend celery_worker 2>&1 | tee -a "$LOG_FILE" || true
        log "Application started (Docker Compose)"
    fi
    
    # Wait for application to be ready
    log "Waiting for application to be ready..."
    sleep 10
    
    # Test application
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Application is healthy"
    else
        log_warning "Application health check failed"
    fi
}

# Cleanup
cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    log "Cleanup completed"
}

# Main execution
main() {
    log "========================================="
    log "Database Restore Started"
    log "========================================="
    
    START_TIME=$(date +%s)
    
    # Run restore process
    check_prerequisites
    download_backup
    verify_backup
    confirm_restore
    backup_current_database
    stop_application
    terminate_connections
    restore_database
    verify_restore
    start_application
    cleanup
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    log "========================================="
    log_success "Database Restore Completed Successfully"
    log "Duration: ${DURATION} seconds"
    log "========================================="
    
    exit 0
}

# Error handler
error_handler() {
    log_error "Restore failed at line $1"
    log_error "Attempting to restart application..."
    start_application
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Run main function
main
