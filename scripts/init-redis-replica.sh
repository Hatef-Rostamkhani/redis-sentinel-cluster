#!/bin/bash

# Redis Replica Initialization Script
# This script reads Docker secrets and generates Redis configuration

set -e

# Read secrets
REDIS_MASTER_PASSWORD=$(cat /run/secrets/redis_master_password 2>/dev/null || echo "redis_master_password_2024")

# Get environment variables
REDIS_MASTER_HOST=${REDIS_MASTER_HOST:-192.168.55.10}
REDIS_MASTER_PORT=${REDIS_MASTER_PORT:-6379}

# Create Redis configuration with secret-based password
cat > /usr/local/etc/redis/redis.conf << EOF
# Redis Replica Configuration
# Port and Network
port 6379
bind 0.0.0.0
protected-mode yes

# Security
requirepass $REDIS_MASTER_PASSWORD
masterauth $REDIS_MASTER_PASSWORD

# Replication
replicaof $REDIS_MASTER_HOST $REDIS_MASTER_PORT
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-ping-replica-period 10
repl-timeout 60
repl-disable-tcp-nodelay no
repl-backlog-size 1mb
repl-backlog-ttl 3600

# Memory and Performance
maxmemory 512mb
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 0

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# AOF (Append Only File)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Logging
loglevel notice
logfile ""
syslog-enabled no

# Slow Log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Latency Monitor
latency-monitor-threshold 100

# Event Notification
notify-keyspace-events ""

# Advanced Config
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
EOF

echo "Redis replica configuration generated with secret-based password"
