#!/bin/bash

# اسکریپت نمایشی failover Redis Sentinel
# ==================================
# این اسکریپت عملکرد failover Redis Sentinel را نمایش می‌دهد

set -e

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

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $1"
}

# بررسی master فعلی
get_current_master() {
    docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel get-master-addr-by-name mymaster 2>/dev/null | head -1
}

# بررسی وضعیت replication
check_replication() {
    local host=$1
    local port=$2
    local password=$3
    local name=$4

    local role=$(docker exec $host redis-cli -p $port -a $password info replication | grep "role:" | cut -d: -f2 | tr -d '\r')
    local master_link=$(docker exec $host redis-cli -p $port -a $password info replication | grep "master_link_status:" | cut -d: -f2 | tr -d '\r' 2>/dev/null || echo "N/A")
    local connected_slaves=$(docker exec $host redis-cli -p $port -a $password info replication | grep "connected_slaves:" | cut -d: -f2 | tr -d '\r' 2>/dev/null || echo "N/A")

    echo "  $name: Role=$role, Master Link=$master_link, Connected Slaves=$connected_slaves"
}

# تابع اصلی demo
main() {
    log "🎬 شروع دمو failover Redis Sentinel"
    echo "========================================"

    # مرحله ۱: نمایش وضعیت اولیه
    log "📊 مرحله ۱: وضعیت اولیه کلاستر"
    echo "--------------------------------"
    
    current_master=$(get_current_master)
    success "Current Master: $current_master"
    
    # بررسی replication برای master فعلی
    current_master=$(get_current_master)
    if [[ "$current_master" == "192.168.55.10" ]]; then
        check_replication "redis-master" "6379" "redis_master_password_2024" "Master"
    elif [[ "$current_master" == "192.168.55.11" ]]; then
        check_replication "redis-replica-1" "6379" "redis_master_password_2024" "Master"
    elif [[ "$current_master" == "192.168.55.12" ]]; then
        check_replication "redis-replica-2" "6379" "redis_master_password_2024" "Master"
    fi
    check_replication "redis-replica-1" "6379" "redis_master_password_2024" "Replica 1"
    check_replication "redis-replica-2" "6379" "redis_master_password_2024" "Replica 2"
    
    # مرحله ۲: نوشتن داده‌های آزمایشی
    log ""
    log "📝 مرحله ۲: نوشتن داده‌های آزمایشی"
    echo "---------------------------"
    
    test_key="failover_demo_$(date +%s)"
    test_value="Data before failover - $(date)"
    
    # نوشتن به master فعلی به جای کانتینر خاص
    current_master=$(get_current_master)
    if [[ "$current_master" == "192.168.55.10" ]]; then
        docker exec redis-master redis-cli -a redis_master_password_2024 set "$test_key" "$test_value" &>/dev/null
    elif [[ "$current_master" == "192.168.55.11" ]]; then
        docker exec redis-replica-1 redis-cli -a redis_master_password_2024 set "$test_key" "$test_value" &>/dev/null
    elif [[ "$current_master" == "192.168.55.12" ]]; then
        docker exec redis-replica-2 redis-cli -a redis_master_password_2024 set "$test_key" "$test_value" &>/dev/null
    fi
    success "Data written to master: $test_key = $test_value"
    
    # Wait for replication
    sleep 3
    
    # Verify replication
    replica1_value=$(docker exec redis-replica-1 redis-cli -a redis_master_password_2024 get "$test_key" 2>/dev/null)
    replica2_value=$(docker exec redis-replica-2 redis-cli -a redis_master_password_2024 get "$test_key" 2>/dev/null)
    
    if [[ "$replica1_value" == "$test_value" && "$replica2_value" == "$test_value" ]]; then
        success "Data replicated to both replicas"
    else
        error "Data replication failed"
        return 1
    fi
    
    # مرحله ۳: شبیه‌سازی خرابی master
    log ""
    log "💥 مرحله ۳: شبیه‌سازی خرابی master"
    echo "-----------------------------------"
    
    warning "Stopping master container..."
    # متوقف کردن کانتینر master فعلی
    current_master=$(get_current_master)
    if [[ "$current_master" == "192.168.55.10" ]]; then
        docker stop redis-master &>/dev/null
    elif [[ "$current_master" == "192.168.55.11" ]]; then
        docker stop redis-replica-1 &>/dev/null
    elif [[ "$current_master" == "192.168.55.12" ]]; then
        docker stop redis-replica-2 &>/dev/null
    fi
    success "Master container stopped"
    
    # مرحله ۴: نظارت بر تشخیص Sentinel
    log ""
    log "👁️ مرحله ۴: نظارت بر تشخیص Sentinel"
    echo "--------------------------------------"
    
    for i in {1..10}; do
        sleep 2
        masters=$(docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters 2>/dev/null || echo "")
        
        if [[ -n "$masters" ]]; then
            # Parse master status
            master_dict=""
            for j in $(seq 0 2 $(echo "$masters" | wc -w)); do
                key=$(echo "$masters" | awk -v j=$j '{print $(j+1)}')
                value=$(echo "$masters" | awk -v j=$j '{print $(j+2)}')
                if [[ -n "$key" && -n "$value" ]]; then
                    master_dict="$master_dict $key=$value"
                fi
            done
            
            if echo "$master_dict" | grep -q "flags.*s_down"; then
                success "Sentinel detected master as down (attempt $i)"
                break
            else
                log "Sentinel still monitoring master (attempt $i)"
            fi
        else
            log "Waiting for Sentinel response (attempt $i)"
        fi
    done
    
    # مرحله ۵: انتظار برای failover
    log ""
    log "⏳ مرحله ۵: انتظار برای failover"
    echo "------------------------------"
    
    for i in {1..15}; do
        sleep 2
        new_master=$(get_current_master)
        
        if [[ -n "$new_master" && "$new_master" != "$current_master" ]]; then
            success "Failover completed! New master: $new_master"
            break
        else
            log "Waiting for failover... (attempt $i/15)"
        fi
    done
    
    # مرحله ۶: تأیید master جدید
    log ""
    log "✅ مرحله ۶: تأیید master جدید"
    echo "------------------------------"
    
    new_master=$(get_current_master)
    if [[ -n "$new_master" ]]; then
        success "New master confirmed: $new_master"
        
        # Test write to new master
        if [[ "$new_master" == "192.168.55.10" ]]; then
            new_master_container="redis-master"
            new_master_password="redis_master_password_2024"
        elif [[ "$new_master" == "192.168.55.11" ]]; then
            new_master_container="redis-replica-1"
            new_master_password="redis_master_password_2024"
        elif [[ "$new_master" == "192.168.55.12" ]]; then
            new_master_container="redis-replica-2"
            new_master_password="redis_master_password_2024"
        else
            error "Unknown new master: $new_master"
            return 1
        fi
        
        # Write to new master
        new_test_value="Data after failover - $(date)"
        docker exec $new_master_container redis-cli -a $new_master_password set "${test_key}_after" "$new_test_value" &>/dev/null
        success "Successfully wrote to new master"
        
        # مرحله ۷: نمایش وضعیت نهایی
        log ""
        log "📊 مرحله ۷: وضعیت نهایی کلاستر"
        echo "-----------------------------"
        
        check_replication "$new_master_container" "6379" "$new_master_password" "New Master"
        check_replication "redis-replica-1" "6379" "redis_master_password_2024" "Replica 1"
        check_replication "redis-replica-2" "6379" "redis_master_password_2024" "Replica 2"
        
        success "🎉 Failover demo completed successfully!"
        
    else
        error "Failover failed - no new master detected"
        return 1
    fi
    
    # مرحله ۸: بازیابی وضعیت اولیه
    log ""
    log "🔄 مرحله ۸: بازیابی وضعیت اولیه"
    echo "----------------------------------"
    
    warning "Restarting original master..."
    # راه‌اندازی مجدد master اصلی (redis-master)
    docker start redis-master &>/dev/null
    sleep 10
    
    # Wait for master to become available
    for i in {1..10}; do
        if docker exec redis-master redis-cli -a redis_master_password_2024 ping &>/dev/null; then
            success "Original master restored"
            break
        else
            log "Waiting for master to start... (attempt $i)"
            sleep 2
        fi
    done
    
    log ""
    success "🎬 دمو تکمیل شد! نتایج را در بالا بررسی کنید."
}

# مدیریت وقفه
trap 'error "Demo interrupted by user"; exit 1' INT

# Run demo
main "$@"
