#!/bin/bash

date=$(date +%Y-%m-%d_%H-%M)

mkdir -p backups

zip -r "backups/backup_$date.zip" . \
    --exclude "venv/*" \
    --exclude ".git/*" \
    --exclude "*__pycache__/*" \
    --exclude "backups/*" \
    --exclude ".env" \
    --exclude ".gitignore" \
    --exclude "discloud.config" \
    --exclude "requirements.txt"

echo "Created backup: backup_$date.zip"