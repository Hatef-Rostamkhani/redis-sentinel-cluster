#!/usr/bin/env python3
"""
Simple Redis Sentinel Test Script
=================================

This script provides basic testing of Redis Sentinel functionality
for high availability and monitoring.

Usage:
    python3 test-sentinel-simple.py
"""

import redis
import sys

def test_sentinel_connections():
    """Test basic Sentinel connectivity"""
    print("🔍 Testing Sentinel connections...")
    
    sentinels = [
        ('localhost', 26379, 'Sentinel 1'),
        ('localhost', 26380, 'Sentinel 2'),
        ('localhost', 26381, 'Sentinel 3')
    ]
    
    all_connected = True
    for host, port, name in sentinels:
        try:
            client = redis.Redis(
                host=host,
                port=port,
                password='redis_sentinel_password_2024',
                decode_responses=True
            )
            result = client.ping()
            print(f"✅ {name} ({port}): {'Connected' if result else 'Failed'}")
            if not result:
                all_connected = False
        except Exception as e:
            print(f"❌ {name} ({port}): Connection failed - {e}")
            all_connected = False
    
    return all_connected

def test_master_monitoring():
    """Test Sentinel master monitoring"""
    print("\n📊 Testing master monitoring...")
    
    try:
        sentinel = redis.Redis(
            host='localhost',
            port=26379,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        # Get master information
        masters = sentinel.execute_command('SENTINEL', 'masters')
        if masters:
            print(f"✅ Found {len(masters)//20} master(s) being monitored")
            
            # Extract key information
            master_info = {}
            for i in range(0, len(masters), 2):
                if i + 1 < len(masters):
                    master_info[masters[i]] = masters[i + 1]
            
            print(f"   Master Name: {master_info.get('name', 'N/A')}")
            print(f"   Master IP: {master_info.get('ip', 'N/A')}")
            print(f"   Master Port: {master_info.get('port', 'N/A')}")
            print(f"   Flags: {master_info.get('flags', 'N/A')}")
            print(f"   Slaves: {master_info.get('num-slaves', 'N/A')}")
            print(f"   Sentinels: {master_info.get('num-other-sentinels', 'N/A')}")
            print(f"   Quorum: {master_info.get('quorum', 'N/A')}")
            
            return True
        else:
            print("❌ No masters found by Sentinel")
            return False
            
    except Exception as e:
        print(f"❌ Master monitoring error: {e}")
        return False

def test_slave_monitoring():
    """Test Sentinel slave monitoring"""
    print("\n📊 Testing slave monitoring...")
    
    try:
        sentinel = redis.Redis(
            host='localhost',
            port=26379,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        # Get slave information
        slaves = sentinel.execute_command('SENTINEL', 'slaves', 'mymaster')
        if slaves:
            # Count slaves by counting 'name' fields
            slave_count = sum(1 for i in range(0, len(slaves), 2) if i < len(slaves) and slaves[i] == 'name')
            print(f"✅ Found {slave_count} slave(s) being monitored")
            
            # Show first slave info
            if slave_count > 0:
                slave_info = {}
                for i in range(0, min(20, len(slaves)), 2):  # First slave has ~20 fields
                    if i + 1 < len(slaves):
                        slave_info[slaves[i]] = slaves[i + 1]
                
                print(f"   First Slave IP: {slave_info.get('ip', 'N/A')}")
                print(f"   First Slave Port: {slave_info.get('port', 'N/A')}")
                print(f"   First Slave Flags: {slave_info.get('flags', 'N/A')}")
            
            return slave_count >= 2
        else:
            print("❌ No slaves found by Sentinel")
            return False
            
    except Exception as e:
        print(f"❌ Slave monitoring error: {e}")
        return False

def test_sentinel_cluster():
    """Test Sentinel cluster communication"""
    print("\n📊 Testing Sentinel cluster...")
    
    try:
        sentinel = redis.Redis(
            host='localhost',
            port=26379,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        # Get other sentinels information
        sentinels = sentinel.execute_command('SENTINEL', 'sentinels', 'mymaster')
        if sentinels:
            # Count sentinels by counting 'name' fields
            sentinel_count = sum(1 for i in range(0, len(sentinels), 2) if i < len(sentinels) and sentinels[i] == 'name')
            print(f"✅ Found {sentinel_count} other Sentinel(s) in cluster")
            
            # Show first sentinel info
            if sentinel_count > 0:
                sentinel_info = {}
                for i in range(0, min(20, len(sentinels)), 2):  # First sentinel has ~20 fields
                    if i + 1 < len(sentinels):
                        sentinel_info[sentinels[i]] = sentinels[i + 1]
                
                print(f"   First Sentinel IP: {sentinel_info.get('ip', 'N/A')}")
                print(f"   First Sentinel Port: {sentinel_info.get('port', 'N/A')}")
                print(f"   First Sentinel Flags: {sentinel_info.get('flags', 'N/A')}")
            
            return sentinel_count >= 2
        else:
            print("❌ No other sentinels found")
            return False
            
    except Exception as e:
        print(f"❌ Sentinel cluster error: {e}")
        return False

def test_master_connectivity():
    """Test direct master connectivity"""
    print("\n🔗 Testing master connectivity...")
    
    try:
        master = redis.Redis(
            host='localhost',
            port=6379,
            password='redis_master_password_2024',
            decode_responses=True
        )
        
        # Test connection
        result = master.ping()
        print(f"✅ Master (6379): {'Connected' if result else 'Failed'}")
        
        if result:
            # Get replication info
            info = master.info('replication')
            role = info.get('role')
            slaves = info.get('connected_slaves')
            
            print(f"   Role: {role}")
            print(f"   Connected Slaves: {slaves}")
            
            return role == 'master' and slaves >= 2
        
        return False
        
    except Exception as e:
        print(f"❌ Master connectivity error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Redis Sentinel Tests")
    print("=" * 50)
    
    tests = [
        ("Sentinel Connections", test_sentinel_connections),
        ("Master Monitoring", test_master_monitoring),
        ("Slave Monitoring", test_slave_monitoring),
        ("Sentinel Cluster", test_sentinel_cluster),
        ("Master Connectivity", test_master_connectivity)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} test passed")
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Redis Sentinel cluster is working correctly.")
        print("\n🔧 Sentinel Cluster Summary:")
        print("   • 3 Sentinel nodes monitoring the cluster")
        print("   • 1 Master node with 2 Replicas")
        print("   • Quorum-based failover capability")
        print("   • High availability and automatic failover")
        return True
    else:
        print("⚠️ Some tests failed. Please check the Sentinel configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
