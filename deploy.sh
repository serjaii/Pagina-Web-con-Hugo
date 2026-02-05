#!/bin/bash
# Deployment Script

# Variables
USER="serjaii"
HOST="sergiojimenez.org"
REMOTE_DIR="/var/www/serjaii"
LOCAL_DIR="./public/"

echo "Deploying to $USER@$HOST:$REMOTE_DIR..."

# Ensure we have the latest build
hugo --minify

# Sync files
# -a: archive mode (preserves permissions, times, etc.)
# -v: verbose
# -z: compress during transfer
# --delete: delete extraneous files from dest dirs
# --rsync-path="sudo rsync": use sudo on the remote machine
rsync -avz --delete --rsync-path="sudo rsync" $LOCAL_DIR $USER@$HOST:$REMOTE_DIR

# Set permissions
ssh $USER@$HOST "sudo chown -R www-data:www-data $REMOTE_DIR && sudo chmod -R 755 $REMOTE_DIR"

echo "Deployment complete!"
