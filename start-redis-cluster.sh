#!/bin/bash

# Redis Cluster Startup Script
# This script starts a Redis cluster with 1 master and 2 replicas

set -e

echo "🚀 Starting Redis Cluster with Docker Compose..."
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create log directory
mkdir -p logs

echo "📁 Creating necessary directories..."
mkdir -p logs

echo "🔧 Starting Redis services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "🔍 Checking service status..."
docker-compose ps

echo "📊 Redis Cluster Status:"
echo "========================"

# Check master status
echo "🔴 Master (Port 6379):"
docker exec redis-master redis-cli -a redis_master_password_2024 info replication | grep -E "(role|connected_slaves|master_replid)"

echo ""
echo "🟢 Replica 1 (Port 6380):"
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 info replication | grep -E "(role|master_host|master_port|master_link_status)"

echo ""
echo "🟢 Replica 2 (Port 6381):"
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 info replication | grep -E "(role|master_host|master_port|master_link_status)"

echo ""
echo "✅ Redis Cluster is ready!"
echo "🌐 Redis Commander (Web UI): http://localhost:8081"
echo ""
echo "📝 Connection Details:"
echo "   Master:   localhost:6379 (Password: redis_master_password_2024)"
echo "   Replica1: localhost:6380 (Password: redis_replica_password_2024)"
echo "   Replica2: localhost:6381 (Password: redis_replica_password_2024)"
echo ""
echo "🔧 Useful Commands:"
echo "   Stop cluster:    docker-compose down"
echo "   View logs:       docker-compose logs -f"
echo "   Restart:         docker-compose restart"
echo "   Scale replicas:  docker-compose up -d --scale redis-replica-1=2"
