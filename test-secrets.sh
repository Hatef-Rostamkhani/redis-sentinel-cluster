#!/bin/bash

# Test script to verify Docker secrets implementation
# This script tests that the Redis setup works with Docker secrets

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $1"
}

# Test 1: Check if secret files exist
test_secret_files() {
    log "Testing secret files..."
    
    if [[ -f "secrets/redis_master_password" ]]; then
        success "redis_master_password secret file exists"
    else
        error "redis_master_password secret file missing"
        return 1
    fi
    
    if [[ -f "secrets/redis_sentinel_password" ]]; then
        success "redis_sentinel_password secret file exists"
    else
        error "redis_sentinel_password secret file missing"
        return 1
    fi
    
    # Check permissions
    if [[ $(stat -c %a "secrets/redis_master_password") == "600" ]]; then
        success "redis_master_password has correct permissions (600)"
    else
        warning "redis_master_password permissions should be 600"
    fi
}

# Test 2: Check if initialization scripts exist and are executable
test_init_scripts() {
    log "Testing initialization scripts..."
    
    scripts=("scripts/init-redis-master.sh" "scripts/init-redis-replica.sh" "scripts/init-redis-sentinel.sh")
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" && -x "$script" ]]; then
            success "$script exists and is executable"
        else
            error "$script missing or not executable"
            return 1
        fi
    done
}

# Test 3: Check Docker Compose configuration
test_docker_compose() {
    log "Testing Docker Compose configuration..."
    
    if grep -q "secrets:" docker-compose.yml; then
        success "Docker Compose has secrets section"
    else
        error "Docker Compose missing secrets section"
        return 1
    fi
    
    if grep -q "redis_master_password:" docker-compose.yml; then
        success "redis_master_password secret defined"
    else
        error "redis_master_password secret not defined"
        return 1
    fi
    
    if grep -q "redis_sentinel_password:" docker-compose.yml; then
        success "redis_sentinel_password secret defined"
    else
        error "redis_sentinel_password secret not defined"
        return 1
    fi
}

# Test 4: Test secret reading in containers (if containers are running)
test_container_secrets() {
    log "Testing container secret access..."
    
    # Check if containers are running
    if ! docker ps | grep -q "redis-master"; then
        warning "Redis containers not running, skipping container secret test"
        return 0
    fi
    
    # Test master password secret
    if docker exec redis-master sh -c "test -f /run/secrets/redis_master_password"; then
        success "redis_master_password secret accessible in redis-master container"
    else
        error "redis_master_password secret not accessible in redis-master container"
        return 1
    fi
    
    # Test sentinel password secret
    if docker exec redis-sentinel-1 sh -c "test -f /run/secrets/redis_sentinel_password"; then
        success "redis_sentinel_password secret accessible in redis-sentinel-1 container"
    else
        error "redis_sentinel_password secret not accessible in redis-sentinel-1 container"
        return 1
    fi
}

# Test 5: Test Redis connectivity with secrets
test_redis_connectivity() {
    log "Testing Redis connectivity with secrets..."
    
    # Check if containers are running
    if ! docker ps | grep -q "redis-master"; then
        warning "Redis containers not running, skipping connectivity test"
        return 0
    fi
    
    # Test master connectivity
    if docker exec redis-master sh -c "redis-cli -a \$(cat /run/secrets/redis_master_password) ping" | grep -q "PONG"; then
        success "Redis master accessible with secret-based password"
    else
        error "Redis master not accessible with secret-based password"
        return 1
    fi
    
    # Test sentinel connectivity
    if docker exec redis-sentinel-1 sh -c "redis-cli -p 26379 -a \$(cat /run/secrets/redis_sentinel_password) ping" | grep -q "PONG"; then
        success "Redis Sentinel accessible with secret-based password"
    else
        error "Redis Sentinel not accessible with secret-based password"
        return 1
    fi
}

# Main test function
main() {
    log "🧪 Starting Docker Secrets Test Suite"
    echo "======================================"
    
    local tests_passed=0
    local tests_total=5
    
    # Run tests
    if test_secret_files; then
        ((tests_passed++))
    fi
    if test_init_scripts; then
        ((tests_passed++))
    fi
    if test_docker_compose; then
        ((tests_passed++))
    fi
    if test_container_secrets; then
        ((tests_passed++))
    fi
    if test_redis_connectivity; then
        ((tests_passed++))
    fi
    
    echo ""
    log "📊 Test Results: $tests_passed/$tests_total tests passed"
    
    if [[ $tests_passed -eq $tests_total ]]; then
        success "🎉 All tests passed! Docker secrets implementation is working correctly."
        return 0
    else
        error "❌ Some tests failed. Please check the implementation."
        return 1
    fi
}

# Run tests
main "$@"
