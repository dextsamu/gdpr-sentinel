#!/bin/sh
set -e
STAMP=$(date +%Y%m%d-%H%M)
mkdir -p /srv/backup
pg_dump "$DATABASE_URL" | gzip > /srv/backup/portale-$STAMP.sql.gz
rclone copy /srv/backup remote:portale-backup
