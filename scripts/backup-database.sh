#!/bin/bash
# Database Backup Script for IndoStar Naturals
# This script creates a backup of the PostgreSQL database and uploads it to S3

set -e

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-indostar_naturals}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
S3_BUCKET="${S3_BUCKET:-s3://indostar-backups-primary}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="indostar_${DATE}.sql.gz"
LOG_FILE="/var/log/backup.log"

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if pg_dump is installed
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump not found. Please install PostgreSQL client."
        exit 1
    fi
    
    # Check if aws CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check if DB_PASSWORD is set
    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD environment variable is not set."
        exit 1
    fi
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    log_success "Prerequisites check passed"
}

# Create backup
create_backup() {
    log "Starting database backup..."
    log "Database: $DB_NAME"
    log "Host: $DB_HOST"
    log "Backup file: $BACKUP_FILE"
    
    # Create backup with pg_dump
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h "$DB_HOST" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="${BACKUP_DIR}/${BACKUP_FILE}" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Backup created successfully"
    else
        log_error "Backup creation failed"
        exit 1
    fi
}

# Verify backup
verify_backup() {
    log "Verifying backup..."
    
    if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
        log_error "Backup file not found: ${BACKUP_DIR}/${BACKUP_FILE}"
        exit 1
    fi
    
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    log "Backup size: $SIZE"
    
    # Check if file is not empty
    if [ ! -s "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
        log_error "Backup file is empty"
        exit 1
    fi
    
    # Verify backup integrity using pg_restore --list
    if PGPASSWORD=$DB_PASSWORD pg_restore --list "${BACKUP_DIR}/${BACKUP_FILE}" > /dev/null 2>&1; then
        log_success "Backup integrity verified"
    else
        log_error "Backup integrity check failed"
        exit 1
    fi
}

# Upload to S3
upload_to_s3() {
    log "Uploading backup to S3..."
    log "Destination: ${S3_BUCKET}/daily/${BACKUP_FILE}"
    
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "${S3_BUCKET}/daily/${BACKUP_FILE}" \
        --storage-class STANDARD_IA \
        --metadata "backup-date=${DATE},database=${DB_NAME}" \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log_success "Backup uploaded to S3"
    else
        log_error "S3 upload failed"
        exit 1
    fi
    
    # Verify upload
    if aws s3 ls "${S3_BUCKET}/daily/${BACKUP_FILE}" > /dev/null 2>&1; then
        log_success "S3 upload verified"
    else
        log_error "S3 upload verification failed"
        exit 1
    fi
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # Clean up local backups (keep only current)
    find "$BACKUP_DIR" -name "indostar_*.sql.gz" -type f ! -name "$BACKUP_FILE" -delete
    log "Local cleanup completed"
    
    # Clean up old S3 backups (keep 30 days)
    CUTOFF_DATE=$(date -d '30 days ago' +%Y%m%d)
    
    aws s3 ls "${S3_BUCKET}/daily/" | while read -r line; do
        FILE_DATE=$(echo "$line" | awk '{print $4}' | grep -oP '\d{8}' | head -1)
        FILE_NAME=$(echo "$line" | awk '{print $4}')
        
        if [ ! -z "$FILE_DATE" ] && [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
            log "Deleting old backup: $FILE_NAME"
            aws s3 rm "${S3_BUCKET}/daily/${FILE_NAME}"
        fi
    done
    
    log_success "Old backups cleaned up"
}

# Send notification
send_notification() {
    STATUS=$1
    MESSAGE=$2
    
    log "Sending notification..."
    
    # Send to monitoring endpoint (if configured)
    if [ ! -z "$NOTIFICATION_URL" ]; then
        curl -X POST "$NOTIFICATION_URL" \
            -H "Content-Type: application/json" \
            -d "{
                \"status\": \"$STATUS\",
                \"message\": \"$MESSAGE\",
                \"backup_file\": \"$BACKUP_FILE\",
                \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
            }" \
            2>&1 | tee -a "$LOG_FILE"
    fi
}

# Main execution
main() {
    log "========================================="
    log "Database Backup Started"
    log "========================================="
    
    START_TIME=$(date +%s)
    
    # Run backup process
    check_prerequisites
    create_backup
    verify_backup
    upload_to_s3
    cleanup_old_backups
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    log "========================================="
    log_success "Database Backup Completed Successfully"
    log "Duration: ${DURATION} seconds"
    log "Backup file: $BACKUP_FILE"
    log "========================================="
    
    send_notification "success" "Database backup completed successfully in ${DURATION} seconds"
    
    exit 0
}

# Error handler
error_handler() {
    log_error "Backup failed at line $1"
    send_notification "failed" "Database backup failed at line $1"
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Run main function
main
