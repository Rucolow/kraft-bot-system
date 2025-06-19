#!/bin/bash

# Setup systemd services for KRAFT Bot System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    error "This script must be run with sudo"
fi

log "Setting up systemd services for KRAFT Bot System..."

# Create logs directory
log "Creating logs directory..."
sudo -u kraftbot mkdir -p /home/kraftbot/kraft-bot-system/logs

# Copy service files
log "Installing systemd service files..."
cp /home/kraftbot/kraft-bot-system/systemd/*.service /etc/systemd/system/

# Reload systemd
log "Reloading systemd daemon..."
systemctl daemon-reload

# Enable services
log "Enabling services..."
for service in kraft-central-bank kraft-community kraft-title kraft-stock-market; do
    systemctl enable $service
    log "Enabled $service"
done

# Start services
log "Starting services..."
for service in kraft-central-bank kraft-community kraft-title kraft-stock-market; do
    systemctl start $service
    log "Started $service"
    sleep 2
done

# Check status
log "Checking service status..."
for service in kraft-central-bank kraft-community kraft-title kraft-stock-market; do
    if systemctl is-active --quiet $service; then
        log "✓ $service is running"
    else
        error "✗ $service failed to start"
    fi
done

log "Setup completed successfully!"
log ""
log "Useful commands:"
log "  systemctl status kraft-*           # Check all bot statuses"
log "  journalctl -u kraft-* -f          # View all bot logs"
log "  systemctl restart kraft-*         # Restart all bots"
log "  systemctl stop kraft-*            # Stop all bots"