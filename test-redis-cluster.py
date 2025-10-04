#!/usr/bin/env python3
"""
Redis Cluster Test Script
This script tests the Redis cluster functionality including master-replica replication
"""

import redis
import time
import sys
from typing import Dict, Any

class RedisClusterTester:
    def __init__(self):
        self.master = redis.Redis(
            host='localhost',
            port=6379,
            password='redis_master_password_2024',
            decode_responses=True
        )
        
        self.replica1 = redis.Redis(
            host='localhost',
            port=6380,
            password='redis_replica_password_2024',
            decode_responses=True
        )
        
        self.replica2 = redis.Redis(
            host='localhost',
            port=6381,
            password='redis_replica_password_2024',
            decode_responses=True
        )
    
    def test_connections(self) -> bool:
        """Test basic connections to all Redis nodes"""
        print("🔍 Testing connections...")
        
        try:
            # Test master connection
            master_info = self.master.ping()
            print(f"✅ Master (6379): {'Connected' if master_info else 'Failed'}")
            
            # Test replica connections
            replica1_info = self.replica1.ping()
            print(f"✅ Replica 1 (6380): {'Connected' if replica1_info else 'Failed'}")
            
            replica2_info = self.replica2.ping()
            print(f"✅ Replica 2 (6381): {'Connected' if replica2_info else 'Failed'}")
            
            return master_info and replica1_info and replica2_info
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def test_replication_status(self) -> Dict[str, Any]:
        """Check replication status of all nodes"""
        print("\n📊 Checking replication status...")
        
        status = {}
        
        try:
            # Master replication info
            master_info = self.master.info('replication')
            status['master'] = {
                'role': master_info.get('role'),
                'connected_slaves': master_info.get('connected_slaves'),
                'master_replid': master_info.get('master_replid')[:8] + '...' if master_info.get('master_replid') else None
            }
            print(f"🔴 Master: Role={status['master']['role']}, Connected Slaves={status['master']['connected_slaves']}")
            
            # Replica 1 info
            replica1_info = self.replica1.info('replication')
            status['replica1'] = {
                'role': replica1_info.get('role'),
                'master_host': replica1_info.get('master_host'),
                'master_port': replica1_info.get('master_port'),
                'master_link_status': replica1_info.get('master_link_status'),
                'master_last_io_seconds_ago': replica1_info.get('master_last_io_seconds_ago')
            }
            print(f"🟢 Replica 1: Role={status['replica1']['role']}, Master Link={status['replica1']['master_link_status']}")
            
            # Replica 2 info
            replica2_info = self.replica2.info('replication')
            status['replica2'] = {
                'role': replica2_info.get('role'),
                'master_host': replica2_info.get('master_host'),
                'master_port': replica2_info.get('master_port'),
                'master_link_status': replica2_info.get('master_link_status'),
                'master_last_io_seconds_ago': replica2_info.get('master_last_io_seconds_ago')
            }
            print(f"🟢 Replica 2: Role={status['replica2']['role']}, Master Link={status['replica2']['master_link_status']}")
            
        except Exception as e:
            print(f"❌ Replication status error: {e}")
        
        return status
    
    def test_read_write_operations(self) -> bool:
        """Test read/write operations and replication"""
        print("\n✍️ Testing read/write operations...")
        
        try:
            # Test data
            test_data = {
                'string_key': 'Hello Redis Cluster!',
                'number_key': 42,
                'list_key': ['item1', 'item2', 'item3'],
                'hash_key': {'field1': 'value1', 'field2': 'value2'}
            }
            
            # Write to master
            print("📝 Writing data to master...")
            self.master.set('string_key', test_data['string_key'])
            self.master.set('number_key', test_data['number_key'])
            self.master.lpush('list_key', *test_data['list_key'])
            self.master.hset('hash_key', mapping=test_data['hash_key'])
            
            # Wait for replication
            print("⏳ Waiting for replication...")
            time.sleep(2)
            
            # Read from replicas
            print("📖 Reading from replicas...")
            
            # Test Replica 1
            replica1_string = self.replica1.get('string_key')
            replica1_number = self.replica1.get('number_key')
            replica1_list = self.replica1.lrange('list_key', 0, -1)
            replica1_hash = self.replica1.hgetall('hash_key')
            
            print(f"Replica 1 - String: {replica1_string}")
            print(f"Replica 1 - Number: {replica1_number}")
            print(f"Replica 1 - List: {replica1_list}")
            print(f"Replica 1 - Hash: {replica1_hash}")
            
            # Test Replica 2
            replica2_string = self.replica2.get('string_key')
            replica2_number = self.replica2.get('number_key')
            replica2_list = self.replica2.lrange('list_key', 0, -1)
            replica2_hash = self.replica2.hgetall('hash_key')
            
            print(f"Replica 2 - String: {replica2_string}")
            print(f"Replica 2 - Number: {replica2_number}")
            print(f"Replica 2 - List: {replica2_list}")
            print(f"Replica 2 - Hash: {replica2_hash}")
            
            # Verify data consistency
            success = (
                replica1_string == test_data['string_key'] and
                replica2_string == test_data['string_key'] and
                int(replica1_number) == test_data['number_key'] and
                int(replica2_number) == test_data['number_key'] and
                set(replica1_list) == set(test_data['list_key']) and
                set(replica2_list) == set(test_data['list_key']) and
                replica1_hash == test_data['hash_key'] and
                replica2_hash == test_data['hash_key']
            )
            
            if success:
                print("✅ All data replicated successfully!")
            else:
                print("❌ Data replication failed!")
            
            return success
            
        except Exception as e:
            print(f"❌ Read/write test error: {e}")
            return False
    
    def test_write_to_replica_fails(self) -> bool:
        """Test that writing to replicas fails (read-only)"""
        print("\n🔒 Testing replica read-only behavior...")
        
        try:
            # Try to write to replica 1 (should fail)
            try:
                self.replica1.set('replica_write_test', 'should_fail')
                print("❌ Replica 1 allowed write operation (should be read-only)")
                return False
            except redis.ResponseError as e:
                if 'READONLY' in str(e):
                    print("✅ Replica 1 correctly rejected write operation")
                else:
                    print(f"❌ Unexpected error from replica 1: {e}")
                    return False
            
            # Try to write to replica 2 (should fail)
            try:
                self.replica2.set('replica_write_test', 'should_fail')
                print("❌ Replica 2 allowed write operation (should be read-only)")
                return False
            except redis.ResponseError as e:
                if 'READONLY' in str(e):
                    print("✅ Replica 2 correctly rejected write operation")
                else:
                    print(f"❌ Unexpected error from replica 2: {e}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Read-only test error: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        try:
            keys_to_delete = ['string_key', 'number_key', 'list_key', 'hash_key']
            for key in keys_to_delete:
                self.master.delete(key)
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 Starting Redis Cluster Tests")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Connections
        if self.test_connections():
            tests_passed += 1
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
            return False
        
        # Test 2: Replication status
        replication_status = self.test_replication_status()
        if (replication_status.get('master', {}).get('role') == 'master' and
            replication_status.get('replica1', {}).get('role') == 'slave' and
            replication_status.get('replica2', {}).get('role') == 'slave'):
            tests_passed += 1
            print("✅ Replication status test passed")
        else:
            print("❌ Replication status test failed")
        
        # Test 3: Read/write operations
        if self.test_read_write_operations():
            tests_passed += 1
            print("✅ Read/write operations test passed")
        else:
            print("❌ Read/write operations test failed")
        
        # Test 4: Replica read-only behavior
        if self.test_write_to_replica_fails():
            tests_passed += 1
            print("✅ Replica read-only test passed")
        else:
            print("❌ Replica read-only test failed")
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Redis cluster is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the cluster configuration.")
            return False

def main():
    """Main function"""
    tester = RedisClusterTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
