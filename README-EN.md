# Redis Cluster with Docker Compose

This project sets up a Redis cluster with one Master and two Replicas using Docker Compose, providing high availability and data replication.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis Master  │    │  Redis Replica1 │    │  Redis Replica2 │
│   Port: 6379    │◄───┤   Port: 6380    │    │   Port: 6381    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Sentinel Cluster                   │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
         │  │ Sentinel 1  │ │ Sentinel 2  │ │ Sentinel 3  │ │
         │  │ Port: 26379 │ │ Port: 26380 │ │ Port: 26381 │ │
         │  └─────────────┘ └─────────────┘ └─────────────┘ │
         └─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.6+ (for testing) - uses virtual environment on Ubuntu 24.04+
- Redis CLI (optional, for manual testing)
- Docker secrets files configured (see Security section)

### Windows
```bash
# Run startup script (manual setup recommended for Windows)
docker-compose up -d
```

### Linux/macOS
```bash
# Make script executable and run
chmod +x start-redis-cluster.sh
./start-redis-cluster.sh
```

### Manual Setup
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Configuration

### Ports
- **Redis Master**: 6379
- **Redis Replica 1**: 6380
- **Redis Replica 2**: 6381
- **Redis Sentinel 1**: 26379
- **Redis Sentinel 2**: 26380
- **Redis Sentinel 3**: 26381
- **RedisInsight**: 8001 (Web UI for Redis management)

### Passwords
- **Master**: `redis_master_password_2024` (configurable via Docker secrets)
- **Replicas**: `redis_replica_password_2024` (configurable via Docker secrets)
- **Sentinels**: `redis_sentinel_password_2024` (configurable via Docker secrets)

### Configuration Files
- `config/redis-master.conf` - Master configuration
- `config/redis-replica-1.conf` - Replica 1 configuration
- `config/redis-replica-2.conf` - Replica 2 configuration
- `config/redis-sentinel-1.conf` - Sentinel 1 configuration
- `config/redis-sentinel-2.conf` - Sentinel 2 configuration
- `config/redis-sentinel-3.conf` - Sentinel 3 configuration

### Initialization Scripts
- `scripts/init-redis-master.sh` - Master initialization script
- `scripts/init-redis-replica.sh` - Replica initialization script
- `scripts/init-redis-sentinel.sh` - Sentinel initialization script

### Docker Secrets
- `secrets/redis_master_password` - Master password file
- `secrets/redis_sentinel_password` - Sentinel password file

## 🔐 Security Features

### 1. Docker Secrets Integration
- Passwords stored in Docker secrets files
- No hardcoded passwords in configuration
- Secure password management following Docker best practices
- Password rotation without container rebuilds

### 2. Authentication
- All nodes protected with strong passwords
- Separate passwords for Master and Replicas
- Protected mode enabled
- Dynamic password loading from secrets

### 3. Network Isolation
- Dedicated Docker network (`redis-network`)
- Internal port restrictions with static IPs
- Bridge network for secure inter-container communication
- Isolated subnet (192.168.55.0/24)

### 4. Data Persistence
- AOF (Append Only File) enabled
- Regular RDB snapshots
- Persistent volumes for data storage
- Data directory isolation per node

### 5. High Availability with Sentinel
- Three Sentinel nodes for quorum-based decisions
- Automatic failover capability
- Master monitoring and health checks
- Service discovery for applications
- Failover timeout and down-after-milliseconds configured

## 📊 Monitoring & Health Checks

### Health Checks
- Automatic health monitoring for all containers
- Service dependency management
- Automatic restart on failure
- Health check intervals: 10s
- Password-aware health checks using Docker secrets

### RedisInsight Web UI
- Modern web-based Redis management interface
- Accessible at http://localhost:8001
- Pre-configured database connections
- Real-time monitoring and administration
- Query interface and performance analytics

### Comprehensive Testing
```bash
# Run Redis cluster test suite
python3 test-redis-cluster.py

# Run Sentinel cluster test suite
python3 test-sentinel-simple.py
```

The test suites include:
- ✅ Connection testing
- ✅ Replication status verification
- ✅ Read/write operations testing
- ✅ Replica read-only behavior validation
- ✅ Sentinel connectivity and monitoring
- ✅ Master/slave discovery by Sentinel
- ✅ Sentinel cluster communication

## 🛠️ Useful Commands

### Demo and Testing Scripts
```bash
# Run Sentinel failover demonstration
demo-sentinel-failover.sh

# Test Redis cluster functionality
python3 test-redis-cluster.py

# Test Sentinel monitoring and HA
python3 test-sentinel-simple.py
```

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f [service-name]
```

### Redis Connections
```bash
# Connect to Master
docker exec -it redis-master redis-cli -a redis_master_password_2024

# Connect to Replica 1
docker exec -it redis-replica-1 redis-cli -a redis_replica_password_2024

# Connect to Replica 2
docker exec -it redis-replica-2 redis-cli -a redis_replica_password_2024

# Connect to Sentinel 1
docker exec -it redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024

# Connect to Sentinel 2
docker exec -it redis-sentinel-2 redis-cli -p 26379 -a redis_sentinel_password_2024

# Connect to Sentinel 3
docker exec -it redis-sentinel-3 redis-cli -p 26379 -a redis_sentinel_password_2024
```

### External Connections
```bash
# Connect to Master from host
redis-cli -h localhost -p 6379 -a redis_master_password_2024

# Connect to Replica 1 from host
redis-cli -h localhost -p 6380 -a redis_replica_password_2024

# Connect to Replica 2 from host
redis-cli -h localhost -p 6381 -a redis_replica_password_2024

# Connect to Sentinel 1 from host
redis-cli -h localhost -p 26379 -a redis_sentinel_password_2024

# Connect to Sentinel 2 from host
redis-cli -h localhost -p 26380 -a redis_sentinel_password_2024

# Connect to Sentinel 3 from host
redis-cli -h localhost -p 26381 -a redis_sentinel_password_2024
```

### Replication Status
```bash
# Check Master status
docker exec redis-master redis-cli -a redis_master_password_2024 info replication

# Check Replica 1 status
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 info replication

# Check Replica 2 status
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 info replication

# Check Sentinel monitoring status
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters

# Check slaves monitored by Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel slaves mymaster

# Check other Sentinels in cluster
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel sentinels mymaster
```

### Performance Testing
```bash
# Write to Master
docker exec redis-master redis-cli -a redis_master_password_2024 set test_key "Hello Redis"

# Read from Replica 1
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 get test_key

# Read from Replica 2
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 get test_key

# Get current master via Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel get-master-addr-by-name mymaster

# Check Sentinel info
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 info sentinel
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check logs
docker-compose logs redis-master
docker-compose logs redis-replica-1
docker-compose logs redis-replica-2
```

#### 2. Replicas Can't Connect to Master
```bash
# Check network
docker network ls
docker network inspect test-docker_redis-network

# Test connectivity
docker exec redis-replica-1 ping redis-master
```

#### 3. Authentication Issues
```bash
# Test connection with password
docker exec redis-master redis-cli -a redis_master_password_2024 ping
```

#### 4. Port Conflicts
```bash
# Check if ports are in use
netstat -tulpn | grep :6379
netstat -tulpn | grep :6380
netstat -tulpn | grep :6381
netstat -tulpn | grep :26379
netstat -tulpn | grep :26380
netstat -tulpn | grep :26381
```

#### 5. Sentinel Issues
```bash
# Check Sentinel logs
docker-compose logs redis-sentinel-1
docker-compose logs redis-sentinel-2
docker-compose logs redis-sentinel-3

# Test Sentinel connectivity
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 ping

# Check Sentinel configuration
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters
```

### Logs
```bash
# View live logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f redis-master
docker-compose logs -f redis-replica-1
docker-compose logs -f redis-sentinel-1
```

## 📈 Performance Optimization

### Memory Settings
- `maxmemory`: 512MB per node
- `maxmemory-policy`: allkeys-lru
- `tcp-keepalive`: 300 seconds

### Replication Settings
- `repl-backlog-size`: 1MB
- `repl-timeout`: 60 seconds
- `repl-ping-replica-period`: 10 seconds
- `repl-diskless-sync`: disabled for stability

### Persistence Settings
- AOF enabled with `appendfsync everysec`
- Regular RDB snapshots
- `auto-aof-rewrite-percentage`: 100%
- `auto-aof-rewrite-min-size`: 64MB

## 🚨 Security Considerations

1. **Change Default Passwords**: Update default passwords for production use
2. **Firewall**: Restrict access to Redis ports
3. **SSL/TLS**: Use SSL for external connections
4. **Monitoring**: Regularly monitor logs and performance
5. **Network Security**: Use VPN or private networks for production

## 📚 Additional Resources

- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [Redis Replication](https://redis.io/topics/replication)
- [Redis Sentinel](https://redis.io/topics/sentinel)
- [Redis Security](https://redis.io/topics/security)
- [Redis Performance](https://redis.io/topics/benchmarks)
- [RedisInsight Documentation](https://docs.redis.com/latest/ri/)

## 📄 Documentation Files

- `README-Docker-Secrets.md` - Detailed Docker secrets implementation guide
- `SECRETS-IMPLEMENTATION-SUMMARY.md` - Summary of security improvements

## 🧪 Testing

The project includes comprehensive test suites and demo scripts that validate:

### Redis Cluster Tests (`test-redis-cluster.py`)
1. **Connection Testing**: Verifies all Redis nodes are accessible
2. **Replication Status**: Confirms master-replica relationships
3. **Data Operations**: Tests read/write operations and replication
4. **Security**: Validates read-only behavior on replicas

### Sentinel Cluster Tests (`test-sentinel-simple.py`)
1. **Sentinel Connectivity**: Verifies all Sentinel nodes are accessible
2. **Master Monitoring**: Confirms Sentinel is monitoring the master
3. **Slave Monitoring**: Validates Sentinel discovery of replicas
4. **Cluster Communication**: Tests Sentinel-to-Sentinel communication
5. **Master Connectivity**: Ensures direct master access works

### Failover Demonstration (`demo-sentinel-failover.sh`)
1. **Live Failover Demo**: Shows real-time Sentinel failover process
2. **Master Promotion**: Demonstrates replica-to-master promotion
3. **Service Recovery**: Tests automatic service restoration
4. **Health Monitoring**: Validates cluster health during failover

Run tests with:
```bash
# Test Redis cluster functionality
python3 test-redis-cluster.py
# Or use the wrapper script (recommended for Ubuntu 24.04+)
./run-tests.sh test-redis-cluster.py

# Test Sentinel monitoring and HA
python3 test-sentinel-simple.py
# Or use the wrapper script (recommended for Ubuntu 24.04+)
./run-tests.sh test-sentinel-simple.py

# Run failover demonstration
./demo-sentinel-failover.sh
```

## 📋 Project Structure

```
test-docker/
├── config/
│   ├── redis-master.conf      # Master configuration
│   ├── redis-replica-1.conf   # Replica 1 configuration
│   ├── redis-replica-2.conf   # Replica 2 configuration
│   ├── redis-sentinel-1.conf  # Sentinel 1 configuration
│   ├── redis-sentinel-2.conf  # Sentinel 2 configuration
│   └── redis-sentinel-3.conf  # Sentinel 3 configuration
├── scripts/
│   ├── init-redis-master.sh   # Master initialization script
│   ├── init-redis-replica.sh  # Replica initialization script
│   └── init-redis-sentinel.sh # Sentinel initialization script
├── secrets/
│   ├── redis_master_password  # Master password secret
│   └── redis_sentinel_password # Sentinel password secret
├── docker-compose.yml         # Docker Compose configuration
├── test-redis-cluster.py      # Redis cluster test suite
├── test-sentinel-simple.py    # Sentinel cluster test suite
├── demo-sentinel-failover.sh  # Failover demonstration script
├── start-redis-cluster.sh     # Linux/macOS startup script
├── requirements.txt           # Python dependencies
├── redisinsight-config.json   # RedisInsight configuration
├── redisinsight-databases.json # RedisInsight database definitions
├── README-Docker-Secrets.md   # Docker secrets documentation
├── README.md                  # Persian documentation
└── README-EN.md              # English documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.
