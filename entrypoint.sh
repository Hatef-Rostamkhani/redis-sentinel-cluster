#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if the first argument is redis-sentinel
if [ "$1" = "redis-sentinel" ]; then
    log "Starting Redis Sentinel..."
    shift
    exec redis-sentinel "$@"
else
    log "Starting Redis server..."
    exec redis-server "$@"
fi
