@echo off
REM Redis Cluster Startup Script for Windows
REM This script starts a Redis cluster with 1 master and 2 replicas

echo 🚀 Starting Redis Cluster with Docker Compose...
echo ================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo 📁 Creating necessary directories...
if not exist "logs" mkdir logs

echo 🔧 Starting Redis services...
docker-compose up -d

echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo 🔍 Checking service status...
docker-compose ps

echo 📊 Redis Cluster Status:
echo ========================

REM Check master status
echo 🔴 Master (Port 6379):
docker exec redis-master redis-cli -a redis_master_password_2024 info replication | findstr /C:"role" /C:"connected_slaves" /C:"master_replid"

echo.
echo 🟢 Replica 1 (Port 6380):
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 info replication | findstr /C:"role" /C:"master_host" /C:"master_port" /C:"master_link_status"

echo.
echo 🟢 Replica 2 (Port 6381):
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 info replication | findstr /C:"role" /C:"master_host" /C:"master_port" /C:"master_link_status"

echo.
echo ✅ Redis Cluster is ready!
echo 🌐 Redis Commander (Web UI): http://localhost:8081
echo.
echo 📝 Connection Details:
echo    Master:   localhost:6379 (Password: redis_master_password_2024)
echo    Replica1: localhost:6380 (Password: redis_replica_password_2024)
echo    Replica2: localhost:6381 (Password: redis_replica_password_2024)
echo.
echo 🔧 Useful Commands:
echo    Stop cluster:    docker-compose down
echo    View logs:       docker-compose logs -f
echo    Restart:         docker-compose restart
echo    Scale replicas:  docker-compose up -d --scale redis-replica-1=2

pause
