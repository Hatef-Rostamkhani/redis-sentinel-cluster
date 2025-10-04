# Redis Docker Secrets Implementation

This document describes the implementation of Docker secrets for password management in the Redis Sentinel setup.

## Overview

The Redis setup has been updated to use Docker secrets instead of hardcoded passwords. This provides better security by:

- Storing passwords in secure files managed by Docker
- Preventing passwords from appearing in container logs or process lists
- Allowing password rotation without rebuilding containers
- Following Docker security best practices

## File Structure

```
├── secrets/
│   ├── redis_master_password      # Redis master/replica password
│   └── redis_sentinel_password    # Redis Sentinel password
├── scripts/
│   ├── init-redis-master.sh       # Master initialization script
│   ├── init-redis-replica.sh      # Replica initialization script
│   └── init-redis-sentinel.sh     # Sentinel initialization script
├── docker-compose.yml             # Updated to use secrets
└── demo-sentinel-failover.sh      # Updated demo script
```

## Secret Files

### redis_master_password
Contains the password used for:
- Redis master authentication (`requirepass`)
- Redis replica authentication (`masterauth`)
- Health checks for Redis instances

### redis_sentinel_password
Contains the password used for:
- Redis Sentinel authentication (`requirepass`)
- Health checks for Sentinel instances

## Initialization Scripts

The initialization scripts read the Docker secrets and generate the appropriate Redis configuration files at runtime:

### init-redis-master.sh
- Reads `redis_master_password` secret
- Generates Redis master configuration with secret-based password
- Sets up replication settings

### init-redis-replica.sh
- Reads `redis_master_password` secret
- Generates Redis replica configuration with secret-based password
- Configures replication to master

### init-redis-sentinel.sh
- Reads both `redis_master_password` and `redis_sentinel_password` secrets
- Generates Sentinel configuration with secret-based passwords
- Configures master monitoring and authentication

## Docker Compose Changes

### Secrets Section
```yaml
secrets:
  redis_master_password:
    file: ./secrets/redis_master_password
  redis_sentinel_password:
    file: ./secrets/redis_sentinel_password
```

### Service Updates
Each service now:
- Mounts the `scripts/` directory
- References appropriate secrets
- Uses initialization scripts in the command
- Updates health checks to read from secrets

Example for Redis master:
```yaml
redis-master:
  volumes:
    - ./scripts:/scripts
  secrets:
    - redis_master_password
  command: >
    sh -c "
      /scripts/init-redis-master.sh &&
      redis-server /usr/local/etc/redis/redis.conf
    "
  healthcheck:
    test: ["CMD", "sh", "-c", "redis-cli -a $$(cat /run/secrets/redis_master_password) ping"]
```

## Usage

### Starting the Stack
```bash
docker-compose up -d
```

### Changing Passwords
1. Update the secret files:
   ```bash
   echo "new_password" > secrets/redis_master_password
   echo "new_sentinel_password" > secrets/redis_sentinel_password
   ```

2. Restart the services:
   ```bash
   docker-compose restart
   ```

### Running the Demo
```bash
./demo-sentinel-failover.sh
```

The demo script has been updated to use Docker secrets for all Redis CLI commands.

### Manual Testing
Use the updated commands in `manual_failover_test.sh` which now read passwords from Docker secrets.

## Security Benefits

1. **No Hardcoded Passwords**: Passwords are no longer visible in configuration files or command lines
2. **Secure Storage**: Docker manages secret file permissions and access
3. **Process Isolation**: Secrets are only accessible to containers that explicitly reference them
4. **Log Safety**: Passwords won't appear in container logs or process lists
5. **Easy Rotation**: Change passwords by updating secret files and restarting services

## Troubleshooting

### Secret File Permissions
Ensure secret files have appropriate permissions:
```bash
chmod 600 secrets/redis_master_password
chmod 600 secrets/redis_sentinel_password
```

### Container Startup Issues
If containers fail to start, check the logs:
```bash
docker-compose logs redis-master
docker-compose logs redis-sentinel-1
```

### Health Check Failures
Health checks now read from secrets. If they fail, verify:
1. Secret files exist and contain valid passwords
2. Secret files are properly mounted in containers
3. Initialization scripts are executable

## Migration from Hardcoded Passwords

The old configuration files in `config/` and `sentinel-configs/` are no longer used. The system now generates configurations dynamically using the initialization scripts and Docker secrets.

## Best Practices

1. **Regular Password Rotation**: Update secret files periodically
2. **Backup Secrets**: Securely backup secret files
3. **Access Control**: Limit access to secret files
4. **Monitoring**: Monitor for unauthorized access to secret files
5. **Documentation**: Keep this documentation updated when making changes
