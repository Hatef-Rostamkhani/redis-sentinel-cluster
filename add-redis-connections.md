# RedisInsight Connection Guide

## Quick Connection Setup for RedisInsight

Open **http://localhost:8001** and add these connections:

### 1. Redis Master
- **Name**: `Redis Master`
- **Host**: `redis-master`
- **Port**: `6379`
- **Password**: `redis_master_password_2024`
- **Database**: `0`

### 2. Redis Replica 1
- **Name**: `Redis Replica 1`
- **Host**: `redis-replica-1`
- **Port**: `6379`
- **Password**: `redis_replica_password_2024`
- **Database**: `0`

### 3. Redis Replica 2
- **Name**: `Redis Replica 2`
- **Host**: `redis-replica-2`
- **Port**: `6379`
- **Password**: `redis_replica_password_2024`
- **Database**: `0`

### 4. Redis Sentinel 1
- **Name**: `Redis Sentinel 1`
- **Host**: `redis-sentinel-1`
- **Port**: `26379`
- **Password**: `redis_sentinel_password_2024`
- **Database**: `0`

### 5. Redis Sentinel 2
- **Name**: `Redis Sentinel 2`
- **Host**: `redis-sentinel-2`
- **Port**: `26380`
- **Password**: `redis_sentinel_password_2024`
- **Database**: `0`

### 6. Redis Sentinel 3
- **Name**: `Redis Sentinel 3`
- **Host**: `redis-sentinel-3`
- **Port**: `26381`
- **Password**: `redis_sentinel_password_2024`
- **Database**: `0`

## What You'll See After Adding Connections

1. **Redis Master**: Shows all your data, keys, and allows write operations
2. **Redis Replicas**: Shows replicated data (read-only)
3. **Redis Sentinels**: Shows monitoring information and cluster status

## Troubleshooting

If a connection fails:
1. Check the host name (use container names, not localhost)
2. Verify the password
3. Ensure the container is running: `docker-compose ps`
