#!/bin/bash

# KRAFT Bot System Deployment Script
# This script should be run on the VPS to deploy updates

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as kraftbot user
if [ "$USER" != "kraftbot" ]; then
    error "This script must be run as kraftbot user"
fi

log "Starting deployment..."

# Navigate to project directory
cd "$PROJECT_DIR" || error "Failed to navigate to project directory"

# Store current commit hash for rollback
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "$CURRENT_COMMIT" > .last_deployment

# Pull latest changes
log "Pulling latest changes from git..."
git fetch origin main
git reset --hard origin/main || error "Failed to pull latest changes"

NEW_COMMIT=$(git rev-parse HEAD)
log "Updated from $CURRENT_COMMIT to $NEW_COMMIT"

# Activate virtual environment
log "Activating virtual environment..."
source kraft_env/bin/activate || error "Failed to activate virtual environment"

# Update dependencies
log "Updating dependencies..."
pip install -r requirements.txt || error "Failed to install dependencies"

# Function to restart services
restart_services() {
    log "Restarting bot services..."
    
    # Check for systemd services
    for service in kraft-central-bank kraft-community kraft-title kraft-stock-market; do
        if systemctl is-enabled "$service" &>/dev/null; then
            log "Restarting $service..."
            sudo systemctl restart "$service" || warn "Failed to restart $service"
            sleep 2
            if systemctl is-active "$service" &>/dev/null; then
                log "$service restarted successfully"
            else
                warn "$service failed to start"
            fi
        fi
    done
    
    # Check for PM2
    if command -v pm2 &> /dev/null; then
        log "Restarting PM2 processes..."
        pm2 restart ecosystem.config.js || pm2 restart all || warn "PM2 restart failed"
    fi
    
    # Check for supervisor
    if command -v supervisorctl &> /dev/null; then
        log "Restarting supervisor processes..."
        supervisorctl restart 'kraft-*' || warn "Supervisor restart failed"
    fi
}

# Check bot status
check_bot_status() {
    log "Checking bot status..."
    
    local all_running=true
    
    # Check Python processes
    for bot in kraft_central_bank kraft_community kraft_title kraft_stock_market; do
        if pgrep -f "${bot}.py" > /dev/null; then
            log "✓ ${bot} is running"
        else
            warn "✗ ${bot} is NOT running"
            all_running=false
        fi
    done
    
    if [ "$all_running" = true ]; then
        log "All bots are running successfully!"
        return 0
    else
        return 1
    fi
}

# Restart services
restart_services

# Wait for services to stabilize
log "Waiting for services to stabilize..."
sleep 10

# Check if all bots are running
if check_bot_status; then
    log "Deployment completed successfully!"
else
    error "Some bots failed to start. Check logs for details."
fi

# Clean up old logs (keep last 30 days)
find "$PROJECT_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

log "Deployment finished at $(date)"