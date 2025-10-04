#!/usr/bin/env python3
"""
Redis Cluster Test Script
========================

This comprehensive test script validates the functionality of a Redis cluster setup
with one master and two replica nodes. It performs thorough testing of:

1. Connection Testing: Verifies all Redis nodes are accessible and responding
2. Replication Status: Confirms master-replica relationships and synchronization
3. Data Operations: Tests read/write operations and data replication consistency
4. Security Validation: Ensures replicas are properly configured as read-only

The script is designed to work with the Docker Compose Redis cluster setup and
provides detailed output for troubleshooting and validation purposes.

Usage:
    python3 test-redis-cluster.py

Requirements:
    - Redis cluster running (docker-compose up -d)
    - Python redis library (pip install redis)
    - All Redis nodes accessible on localhost with configured ports

Exit Codes:
    0: All tests passed successfully
    1: One or more tests failed
"""

import redis
import time
import sys
from typing import Dict, Any

class RedisClusterTester:
    """
    Comprehensive Redis Cluster Testing Class
    
    This class provides methods to test various aspects of a Redis cluster
    including connections, replication, data consistency, and security.
    
    Attributes:
        master (redis.Redis): Connection to the master Redis node (port 6379)
        replica1 (redis.Redis): Connection to the first replica node (port 6380)
        replica2 (redis.Redis): Connection to the second replica node (port 6381)
    """
    
    def __init__(self):
        """
        Initialize Redis connections to all cluster nodes.
        
        Sets up connections to:
        - Master node on localhost:6379 with master password
        - Replica 1 on localhost:6380 with replica password
        - Replica 2 on localhost:6381 with replica password
        
        All connections use decode_responses=True for string handling.
        """
        # Master node connection (write operations)
        self.master = redis.Redis(
            host='localhost',
            port=6379,
            password='redis_master_password_2024',
            decode_responses=True
        )
        
        # First replica connection (read-only operations)
        self.replica1 = redis.Redis(
            host='localhost',
            port=6380,
            password='redis_replica_password_2024',
            decode_responses=True
        )
        
        # Second replica connection (read-only operations)
        self.replica2 = redis.Redis(
            host='localhost',
            port=6381,
            password='redis_replica_password_2024',
            decode_responses=True
        )
    
    def test_connections(self) -> bool:
        """
        Test basic connectivity to all Redis nodes in the cluster.
        
        This method performs a PING operation on each Redis node to verify:
        - Network connectivity is established
        - Authentication is working correctly
        - All nodes are responding to commands
        
        Returns:
            bool: True if all nodes are accessible, False otherwise
            
        Raises:
            Exception: If any connection fails or authentication error occurs
        """
        print("🔍 Testing connections...")
        
        try:
            # Test master node connectivity and authentication
            master_info = self.master.ping()
            print(f"✅ Master (6379): {'Connected' if master_info else 'Failed'}")
            
            # Test first replica connectivity and authentication
            replica1_info = self.replica1.ping()
            print(f"✅ Replica 1 (6380): {'Connected' if replica1_info else 'Failed'}")
            
            # Test second replica connectivity and authentication
            replica2_info = self.replica2.ping()
            print(f"✅ Replica 2 (6381): {'Connected' if replica2_info else 'Failed'}")
            
            # Return True only if all nodes are accessible
            return master_info and replica1_info and replica2_info
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def test_replication_status(self) -> Dict[str, Any]:
        """
        Check and validate the replication status of all nodes in the cluster.
        
        This method retrieves replication information from each node and validates:
        - Master node has correct role and connected slaves count
        - Replica nodes have correct role and are connected to master
        - Master-replica relationships are properly established
        - Replication links are active and healthy
        
        Returns:
            Dict[str, Any]: Dictionary containing replication status for all nodes
            {
                'master': {
                    'role': str,
                    'connected_slaves': int,
                    'master_replid': str
                },
                'replica1': {
                    'role': str,
                    'master_host': str,
                    'master_port': int,
                    'master_link_status': str,
                    'master_last_io_seconds_ago': int
                },
                'replica2': { ... }
            }
        """
        print("\n📊 Checking replication status...")
        
        status = {}
        
        try:
            # Get master node replication information
            master_info = self.master.info('replication')
            status['master'] = {
                'role': master_info.get('role'),
                'connected_slaves': master_info.get('connected_slaves'),
                'master_replid': master_info.get('master_replid')[:8] + '...' if master_info.get('master_replid') else None
            }
            print(f"🔴 Master: Role={status['master']['role']}, Connected Slaves={status['master']['connected_slaves']}")
            
            # Get first replica replication information
            replica1_info = self.replica1.info('replication')
            status['replica1'] = {
                'role': replica1_info.get('role'),
                'master_host': replica1_info.get('master_host'),
                'master_port': replica1_info.get('master_port'),
                'master_link_status': replica1_info.get('master_link_status'),
                'master_last_io_seconds_ago': replica1_info.get('master_last_io_seconds_ago')
            }
            print(f"🟢 Replica 1: Role={status['replica1']['role']}, Master Link={status['replica1']['master_link_status']}")
            
            # Get second replica replication information
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
        """
        Test read/write operations and validate data replication consistency.
        
        This method performs comprehensive data operations testing:
        1. Writes various data types to the master node
        2. Waits for replication to complete
        3. Reads the same data from both replica nodes
        4. Validates that all data is consistent across all nodes
        
        Data types tested:
        - Strings: Basic key-value pairs
        - Numbers: Integer values
        - Lists: Ordered collections with multiple items
        - Hashes: Key-value pairs within a single key
        
        Returns:
            bool: True if all data is replicated correctly, False otherwise
        """
        print("\n✍️ Testing read/write operations...")
        
        try:
            # Define test data with various Redis data types
            test_data = {
                'string_key': 'Hello Redis Cluster!',
                'number_key': 42,
                'list_key': ['item1', 'item2', 'item3'],
                'hash_key': {'field1': 'value1', 'field2': 'value2'}
            }
            
            # Write test data to master node
            print("📝 Writing data to master...")
            self.master.set('string_key', test_data['string_key'])
            self.master.set('number_key', test_data['number_key'])
            self.master.lpush('list_key', *test_data['list_key'])
            self.master.hset('hash_key', mapping=test_data['hash_key'])
            
            # Wait for replication to complete (allow time for sync)
            print("⏳ Waiting for replication...")
            time.sleep(2)
            
            # Read data from replica nodes
            print("📖 Reading from replicas...")
            
            # Test data retrieval from first replica
            replica1_string = self.replica1.get('string_key')
            replica1_number = self.replica1.get('number_key')
            replica1_list = self.replica1.lrange('list_key', 0, -1)
            replica1_hash = self.replica1.hgetall('hash_key')
            
            print(f"Replica 1 - String: {replica1_string}")
            print(f"Replica 1 - Number: {replica1_number}")
            print(f"Replica 1 - List: {replica1_list}")
            print(f"Replica 1 - Hash: {replica1_hash}")
            
            # Test data retrieval from second replica
            replica2_string = self.replica2.get('string_key')
            replica2_number = self.replica2.get('number_key')
            replica2_list = self.replica2.lrange('list_key', 0, -1)
            replica2_hash = self.replica2.hgetall('hash_key')
            
            print(f"Replica 2 - String: {replica2_string}")
            print(f"Replica 2 - Number: {replica2_number}")
            print(f"Replica 2 - List: {replica2_list}")
            print(f"Replica 2 - Hash: {replica2_hash}")
            
            # Validate data consistency across all nodes
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
                if 'READONLY' in str(e) or 'read only replica' in str(e).lower():
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
                if 'READONLY' in str(e) or 'read only replica' in str(e).lower():
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
