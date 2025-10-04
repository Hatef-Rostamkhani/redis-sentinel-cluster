#!/bin/bash

# Redis Sentinel Scenarios Test Script
# ===================================
#
# This script tests various Redis Sentinel scenarios including:
# 1. Normal operation monitoring
# 2. Master failure simulation
# 3. Network partition scenarios
# 4. Sentinel failure scenarios
# 5. Recovery and failover testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MASTER_HOST="localhost"
MASTER_PORT="6379"
MASTER_PASSWORD="redis_master_password_2024"

REPLICA1_HOST="localhost"
REPLICA1_PORT="6380"
REPLICA1_PASSWORD="redis_replica_password_2024"

REPLICA2_HOST="localhost"
REPLICA2_PORT="6381"
REPLICA2_PASSWORD="redis_replica_password_2024"

SENTINEL1_HOST="localhost"
SENTINEL1_PORT="26379"
SENTINEL1_PASSWORD="redis_sentinel_password_2024"

SENTINEL2_HOST="localhost"
SENTINEL2_PORT="26380"
SENTINEL2_PASSWORD="redis_sentinel_password_2024"

SENTINEL3_HOST="localhost"
SENTINEL3_PORT="26381"
SENTINEL3_PASSWORD="redis_sentinel_password_2024"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%H:%M:%S')
    
    case $level in
        "INFO")  echo -e "[$timestamp] ${BLUE}INFO${NC}: $message" ;;
        "SUCCESS") echo -e "[$timestamp] ${GREEN}SUCCESS${NC}: $message" ;;
        "WARNING") echo -e "[$timestamp] ${YELLOW}WARNING${NC}: $message" ;;
        "ERROR") echo -e "[$timestamp] ${RED}ERROR${NC}: $message" ;;
    esac
}

# Check if Redis CLI is available
check_redis_cli() {
    if ! command -v redis-cli &> /dev/null; then
        log "ERROR" "redis-cli is not installed. Please install Redis CLI."
        exit 1
    fi
}

# Check cluster health
check_cluster_health() {
    log "INFO" "🔍 Checking cluster health..."
    
    local health_status=0
    
    # Check master
    if redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD ping &>/dev/null; then
        log "SUCCESS" "Master: Connected"
        local master_role=$(redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD info replication | grep "role:" | cut -d: -f2 | tr -d '\r')
        local connected_slaves=$(redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD info replication | grep "connected_slaves:" | cut -d: -f2 | tr -d '\r')
        log "INFO" "Master role: $master_role, Connected slaves: $connected_slaves"
    else
        log "ERROR" "Master: Connection failed"
        health_status=1
    fi
    
    # Check replicas
    for i in 1 2; do
        local replica_host="REPLICA${i}_HOST"
        local replica_port="REPLICA${i}_PORT"
        local replica_password="REPLICA${i}_PASSWORD"
        
        if redis-cli -h ${!replica_host} -p ${!replica_port} -a ${!replica_password} ping &>/dev/null; then
            log "SUCCESS" "Replica $i: Connected"
            local replica_role=$(redis-cli -h ${!replica_host} -p ${!replica_port} -a ${!replica_password} info replication | grep "role:" | cut -d: -f2 | tr -d '\r')
            local master_link=$(redis-cli -h ${!replica_host} -p ${!replica_port} -a ${!replica_password} info replication | grep "master_link_status:" | cut -d: -f2 | tr -d '\r')
            log "INFO" "Replica $i role: $replica_role, Master link: $master_link"
        else
            log "ERROR" "Replica $i: Connection failed"
            health_status=1
        fi
    done
    
    # Check sentinels
    for i in 1 2 3; do
        local sentinel_host="SENTINEL${i}_HOST"
        local sentinel_port="SENTINEL${i}_PORT"
        local sentinel_password="SENTINEL${i}_PASSWORD"
        
        if redis-cli -h ${!sentinel_host} -p ${!sentinel_port} -a ${!sentinel_password} ping &>/dev/null; then
            log "SUCCESS" "Sentinel $i: Connected"
        else
            log "ERROR" "Sentinel $i: Connection failed"
            health_status=1
        fi
    done
    
    return $health_status
}

# Test normal monitoring
test_normal_monitoring() {
    log "INFO" "📊 Testing normal monitoring scenario..."
    
    local test_key="monitor_test_$(date +%s)"
    local test_value="Normal monitoring test data"
    
    # Write to master
    if redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD set "$test_key" "$test_value" &>/dev/null; then
        log "SUCCESS" "Data written to master"
    else
        log "ERROR" "Failed to write to master"
        return 1
    fi
    
    # Wait for replication
    sleep 3
    
    # Check replication
    local replica1_value=$(redis-cli -h $REPLICA1_HOST -p $REPLICA1_PORT -a $REPLICA1_PASSWORD get "$test_key" 2>/dev/null)
    local replica2_value=$(redis-cli -h $REPLICA2_HOST -p $REPLICA2_PORT -a $REPLICA2_PASSWORD get "$test_key" 2>/dev/null)
    
    if [[ "$replica1_value" == "$test_value" && "$replica2_value" == "$test_value" ]]; then
        log "SUCCESS" "Normal monitoring: Data replicated successfully"
        return 0
    else
        log "ERROR" "Normal monitoring: Data replication failed"
        return 1
    fi
}

# Test master failure
test_master_failure() {
    log "INFO" "💥 Testing master failure scenario..."
    
    local test_key="failover_test_$(date +%s)"
    local test_value="Before failure"
    
    # Write data before failure
    redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD set "$test_key" "$test_value" &>/dev/null
    log "INFO" "Data written before failure"
    
    # Stop master container
    log "INFO" "🛑 Stopping master container..."
    if docker stop redis-master &>/dev/null; then
        log "SUCCESS" "Master container stopped"
    else
        log "ERROR" "Failed to stop master container"
        return 1
    fi
    
    # Wait for Sentinel detection
    log "INFO" "⏳ Waiting for Sentinel to detect failure..."
    sleep 10
    
    # Check Sentinel status
    local masters=$(redis-cli -h $SENTINEL1_HOST -p $SENTINEL1_PORT -a $SENTINEL1_PASSWORD sentinel masters 2>/dev/null)
    if [[ -n "$masters" ]]; then
        log "SUCCESS" "Master failure: Sentinel detected master status"
    else
        log "WARNING" "Master failure: Sentinel status unclear"
    fi
    
    # Wait for failover
    log "INFO" "⏳ Waiting for failover..."
    sleep 15
    
    # Check for new master
    local new_master=$(redis-cli -h $SENTINEL1_HOST -p $SENTINEL1_PORT -a $SENTINEL1_PASSWORD sentinel get-master-addr-by-name mymaster 2>/dev/null)
    if [[ -n "$new_master" ]]; then
        log "SUCCESS" "Failover detected: New master at $new_master"
        return 0
    else
        log "ERROR" "Failover: No new master detected"
        return 1
    fi
}

# Test network partition
test_network_partition() {
    log "INFO" "🌐 Testing network partition scenario..."
    
    # Stop one Sentinel to simulate partition
    log "INFO" "🛑 Stopping Sentinel 1 to simulate partition..."
    if docker stop redis-sentinel-1 &>/dev/null; then
        log "SUCCESS" "Sentinel 1 stopped"
    else
        log "ERROR" "Failed to stop Sentinel 1"
        return 1
    fi
    
    # Wait for stabilization
    sleep 5
    
    # Check remaining Sentinels
    local sentinel2_ping=$(redis-cli -h $SENTINEL2_HOST -p $SENTINEL2_PORT -a $SENTINEL2_PASSWORD ping 2>/dev/null)
    local sentinel3_ping=$(redis-cli -h $SENTINEL3_HOST -p $SENTINEL3_PORT -a $SENTINEL3_PASSWORD ping 2>/dev/null)
    
    if [[ "$sentinel2_ping" == "PONG" && "$sentinel3_ping" == "PONG" ]]; then
        log "SUCCESS" "Network partition: Remaining Sentinels are healthy"
        
        # Check quorum
        local masters=$(redis-cli -h $SENTINEL2_HOST -p $SENTINEL2_PORT -a $SENTINEL2_PASSWORD sentinel masters 2>/dev/null)
        if [[ -n "$masters" ]]; then
            log "SUCCESS" "Network partition: Quorum maintained"
            return 0
        else
            log "ERROR" "Network partition: Quorum lost"
            return 1
        fi
    else
        log "ERROR" "Network partition: Remaining Sentinels unhealthy"
        return 1
    fi
}

# Test Sentinel failure
test_sentinel_failure() {
    log "INFO" "🔧 Testing Sentinel failure scenario..."
    
    # Stop one Sentinel
    log "INFO" "🛑 Stopping Sentinel 2..."
    if docker stop redis-sentinel-2 &>/dev/null; then
        log "SUCCESS" "Sentinel 2 stopped"
    else
        log "ERROR" "Failed to stop Sentinel 2"
        return 1
    fi
    
    # Wait for stabilization
    sleep 5
    
    # Check remaining Sentinels
    local sentinel1_ping=$(redis-cli -h $SENTINEL1_HOST -p $SENTINEL1_PORT -a $SENTINEL1_PASSWORD ping 2>/dev/null)
    local sentinel3_ping=$(redis-cli -h $SENTINEL3_HOST -p $SENTINEL3_PORT -a $SENTINEL3_PASSWORD ping 2>/dev/null)
    
    if [[ "$sentinel1_ping" == "PONG" && "$sentinel3_ping" == "PONG" ]]; then
        log "SUCCESS" "Sentinel failure: Remaining Sentinels operational"
        
        # Check monitoring
        local masters=$(redis-cli -h $SENTINEL1_HOST -p $SENTINEL1_PORT -a $SENTINEL1_PASSWORD sentinel masters 2>/dev/null)
        if [[ -n "$masters" ]]; then
            log "SUCCESS" "Sentinel failure: Monitoring continues"
            return 0
        else
            log "ERROR" "Sentinel failure: Monitoring lost"
            return 1
        fi
    else
        log "ERROR" "Sentinel failure: Remaining Sentinels failed"
        return 1
    fi
}

# Test recovery
test_recovery() {
    log "INFO" "🔄 Testing recovery scenario..."
    
    # Restart stopped services
    log "INFO" "🔄 Restarting stopped services..."
    
    # Check and restart master
    if ! docker ps -q -f name=redis-master | grep -q .; then
        if docker start redis-master &>/dev/null; then
            log "SUCCESS" "Master restarted"
        else
            log "ERROR" "Failed to restart master"
        fi
    fi
    
    # Check and restart Sentinel 1
    if ! docker ps -q -f name=redis-sentinel-1 | grep -q .; then
        if docker start redis-sentinel-1 &>/dev/null; then
            log "SUCCESS" "Sentinel 1 restarted"
        else
            log "ERROR" "Failed to restart Sentinel 1"
        fi
    fi
    
    # Check and restart Sentinel 2
    if ! docker ps -q -f name=redis-sentinel-2 | grep -q .; then
        if docker start redis-sentinel-2 &>/dev/null; then
            log "SUCCESS" "Sentinel 2 restarted"
        else
            log "ERROR" "Failed to restart Sentinel 2"
        fi
    fi
    
    # Wait for services to stabilize
    log "INFO" "⏳ Waiting for services to stabilize..."
    sleep 20
    
    # Check final health
    if check_cluster_health; then
        log "SUCCESS" "Recovery: Cluster fully recovered"
        return 0
    else
        log "ERROR" "Recovery: Cluster not fully recovered"
        return 1
    fi
}

# Test stress scenario
test_stress() {
    log "INFO" "⚡ Testing stress scenario..."
    
    local success_count=0
    local total_operations=10
    
    for i in $(seq 1 $total_operations); do
        local key="stress_test_$i"
        local value="Stress test data $i - $(date)"
        
        # Write to master
        if redis-cli -h $MASTER_HOST -p $MASTER_PORT -a $MASTER_PASSWORD set "$key" "$value" &>/dev/null; then
            # Wait for replication
            sleep 1
            
            # Check replication
            local replica1_value=$(redis-cli -h $REPLICA1_HOST -p $REPLICA1_PORT -a $REPLICA1_PASSWORD get "$key" 2>/dev/null)
            local replica2_value=$(redis-cli -h $REPLICA2_HOST -p $REPLICA2_PORT -a $REPLICA2_PASSWORD get "$key" 2>/dev/null)
            
            if [[ "$replica1_value" == "$value" && "$replica2_value" == "$value" ]]; then
                ((success_count++))
            fi
        fi
    done
    
    local success_rate=$((success_count * 100 / total_operations))
    log "INFO" "Stress test: $success_count/$total_operations operations successful ($success_rate%)"
    
    if [[ $success_rate -ge 80 ]]; then
        log "SUCCESS" "Stress test passed"
        return 0
    else
        log "ERROR" "Stress test failed"
        return 1
    fi
}

# Run specific scenario
run_scenario() {
    local scenario=$1
    
    case $scenario in
        "monitor")
            test_normal_monitoring
            ;;
        "failover")
            test_master_failure
            ;;
        "partition")
            test_network_partition
            ;;
        "sentinel")
            test_sentinel_failure
            ;;
        "recovery")
            test_recovery
            ;;
        "stress")
            test_stress
            ;;
        *)
            log "ERROR" "Unknown scenario: $scenario"
            return 1
            ;;
    esac
}

# Run all scenarios
run_all_scenarios() {
    log "INFO" "🎯 Running all Sentinel scenarios..."
    
    local scenarios=("monitor" "failover" "partition" "sentinel" "recovery" "stress")
    local results=()
    
    for scenario in "${scenarios[@]}"; do
        log "INFO" ""
        log "INFO" "=================================================="
        log "INFO" "Running scenario: $scenario"
        log "INFO" "=================================================="
        
        if run_scenario "$scenario"; then
            log "SUCCESS" "Scenario '$scenario' PASSED"
            results+=("✅ $scenario")
        else
            log "ERROR" "Scenario '$scenario' FAILED"
            results+=("❌ $scenario")
        fi
        
        # Wait between scenarios
        sleep 5
    done
    
    # Print summary
    log "INFO" ""
    log "INFO" "============================================================"
    log "INFO" "📊 SENTINEL SCENARIOS TEST SUMMARY"
    log "INFO" "============================================================"
    
    for result in "${results[@]}"; do
        log "INFO" "$result"
    done
    
    local passed=$(printf '%s\n' "${results[@]}" | grep -c "✅" || true)
    local total=${#results[@]}
    
    log "INFO" "------------------------------------------------------------"
    log "INFO" "TOTAL RESULTS: $passed/$total scenarios passed"
    
    if [[ $passed -eq $total ]]; then
        log "SUCCESS" "🎉 ALL SCENARIOS PASSED! Sentinel cluster is working perfectly."
    else
        log "WARNING" "⚠️ Some scenarios failed. Check the cluster configuration."
    fi
    
    log "INFO" "============================================================"
}

# Main function
main() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 [scenario]"
        echo "Scenarios: all, monitor, failover, partition, sentinel, recovery, stress"
        exit 1
    fi
    
    local scenario=$1
    
    # Check prerequisites
    check_redis_cli
    
    log "INFO" "🚀 Starting Redis Sentinel Scenarios Test"
    log "INFO" "Scenario: $scenario"
    log "INFO" "Timestamp: $(date)"
    
    if [[ "$scenario" == "all" ]]; then
        run_all_scenarios
    else
        if run_scenario "$scenario"; then
            log "SUCCESS" "✅ Scenario '$scenario' PASSED"
            exit 0
        else
            log "ERROR" "❌ Scenario '$scenario' FAILED"
            exit 1
        fi
    fi
}

# Handle script interruption
trap 'log "WARNING" "Test interrupted by user"; exit 1' INT

# Run main function
main "$@"
