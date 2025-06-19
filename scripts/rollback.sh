#!/bin/bash

# KRAFT Bot System Rollback Script
# This script rolls back to the previous deployment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/rollback.log"

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

# Check if running as kraftbot user
if [ "$USER" != "kraftbot" ]; then
    error "This script must be run as kraftbot user"
fi

log "Starting rollback..."

# Navigate to project directory
cd "$PROJECT_DIR" || error "Failed to navigate to project directory"

# Check if we have a previous deployment record
if [ ! -f .last_deployment ]; then
    error "No previous deployment found. Cannot rollback."
fi

PREVIOUS_COMMIT=$(cat .last_deployment)
CURRENT_COMMIT=$(git rev-parse HEAD)

log "Rolling back from $CURRENT_COMMIT to $PREVIOUS_COMMIT"

# Rollback to previous commit
git reset --hard "$PREVIOUS_COMMIT" || error "Failed to rollback to previous commit"

# Activate virtual environment
log "Activating virtual environment..."
source kraft_env/bin/activate || error "Failed to activate virtual environment"

# Restore dependencies
log "Restoring dependencies..."
pip install -r requirements.txt || error "Failed to install dependencies"

# Restart services using the deploy script's function
bash "$SCRIPT_DIR/deploy.sh" || error "Failed to restart services"

log "Rollback completed successfully!"