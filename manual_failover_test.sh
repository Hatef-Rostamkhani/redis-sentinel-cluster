# Manual Sentinel Failover Test Instructions

## Current Status
name
mymaster
ip
192.168.55.12
port
6379
runid
6e981cccc70b4097d5cf381266bebef73d013761
flags
master
link-pending-commands
0
link-refcount
1
last-ping-sent
0
last-ok-ping-reply
381
last-ping-reply
381
down-after-milliseconds
5000
info-refresh
3968
role-reported
master
role-reported-time
24035
config-epoch
9
num-slaves
2
num-other-sentinels
2
quorum
2
failover-timeout
10000
parallel-syncs
1

## Step 1: Check current master
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel get-master-addr-by-name mymaster

## Step 2: Write test data to current master
docker exec redis-master redis-cli -a redis_master_password_2024 set manual_failover_test 'Sat Oct  4 17:29:04 +0330 2025' 

## Step 3: Verify data is replicated
docker exec redis-replica-1 redis-cli -a redis_master_password_2024 get manual_failover_test
docker exec redis-replica-2 redis-cli -a redis_master_password_2024 get manual_failover_test

## Step 4: Stop current master
docker stop redis-master

## Step 5: Monitor failover (check every 5 seconds)
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel get-master-addr-by-name mymaster

## Step 6: Once failover completes, verify new master
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters

## Step 7: Write to new master to verify it works
# (Determine new master from step 6, then write to it)

## Step 8: Restore original master
docker start redis-master
