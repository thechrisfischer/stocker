#!/bin/bash
# Daily SQLite backup script - add to crontab:
#   0 2 * * * /opt/stocker/deploy/backup.sh
#
# Prerequisites: aws cli configured with credentials

set -euo pipefail

DB_PATH="/opt/stocker/data/stocker.db"
BACKUP_DIR="/tmp"
S3_BUCKET="${S3_BACKUP_BUCKET:-your-backup-bucket}"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/stocker-$DATE.db"

if [ ! -f "$DB_PATH" ]; then
    echo "Database file not found: $DB_PATH"
    exit 1
fi

# Use SQLite's built-in backup (safe for concurrent access)
sqlite3 "$DB_PATH" ".backup $BACKUP_FILE"

# Upload to S3
aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/backups/stocker-$DATE.db"

# Clean up local backup
rm -f "$BACKUP_FILE"

# Remove S3 backups older than 30 days
aws s3 ls "s3://$S3_BUCKET/backups/" | while read -r line; do
    file_date=$(echo "$line" | awk '{print $1}')
    file_name=$(echo "$line" | awk '{print $4}')
    if [ -n "$file_name" ]; then
        file_epoch=$(date -d "$file_date" +%s 2>/dev/null || echo 0)
        cutoff_epoch=$(date -d "30 days ago" +%s)
        if [ "$file_epoch" -lt "$cutoff_epoch" ] && [ "$file_epoch" -gt 0 ]; then
            aws s3 rm "s3://$S3_BUCKET/backups/$file_name"
        fi
    fi
done

echo "Backup completed: stocker-$DATE.db"
