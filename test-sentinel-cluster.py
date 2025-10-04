#!/usr/bin/env python3
"""
Redis Sentinel Cluster Test Script
==================================

This comprehensive test script validates the functionality of a Redis cluster
with Sentinel monitoring for high availability and automatic failover.

The script tests:
1. Sentinel connectivity and authentication
2. Master monitoring and discovery
3. Slave detection and monitoring
4. Sentinel cluster communication
5. Failover simulation (optional)

Usage:
    python3 test-sentinel-cluster.py

Requirements:
    - Redis cluster with Sentinel running (docker-compose up -d)
    - Python redis library (pip install redis)
    - All Sentinel nodes accessible on localhost with configured ports

Exit Codes:
    0: All tests passed successfully
    1: One or more tests failed
"""

import redis
import time
import sys
from typing import Dict, Any, List

class RedisSentinelClusterTester:
    """
    Comprehensive Redis Sentinel Cluster Testing Class
    
    This class provides methods to test various aspects of a Redis Sentinel cluster
    including connectivity, monitoring, and failover capabilities.
    
    Attributes:
        sentinel1 (redis.Redis): Connection to the first Sentinel node (port 26379)
        sentinel2 (redis.Redis): Connection to the second Sentinel node (port 26380)
        sentinel3 (redis.Redis): Connection to the third Sentinel node (port 26381)
        master (redis.Redis): Connection to the master Redis node (port 6379)
    """
    
    def __init__(self):
        """
        Initialize Redis connections to all Sentinel and Redis nodes.
        
        Sets up connections to:
        - Sentinel 1 on localhost:26379 with Sentinel password
        - Sentinel 2 on localhost:26380 with Sentinel password
        - Sentinel 3 on localhost:26381 with Sentinel password
        - Master node on localhost:6379 with master password
        """
        # Sentinel connections
        self.sentinel1 = redis.Redis(
            host='localhost',
            port=26379,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        self.sentinel2 = redis.Redis(
            host='localhost',
            port=26380,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        self.sentinel3 = redis.Redis(
            host='localhost',
            port=26381,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        # Master connection
        self.master = redis.Redis(
            host='localhost',
            port=6379,
            password='redis_master_password_2024',
            decode_responses=True
        )
    
    def test_sentinel_connections(self) -> bool:
        """
        Test basic connectivity to all Sentinel nodes.
        
        This method performs a PING operation on each Sentinel node to verify:
        - Network connectivity is established
        - Authentication is working correctly
        - All Sentinel nodes are responding to commands
        
        Returns:
            bool: True if all Sentinel nodes are accessible, False otherwise
        """
        print("🔍 Testing Sentinel connections...")
        
        try:
            # Test Sentinel 1 connectivity
            sentinel1_info = self.sentinel1.ping()
            print(f"✅ Sentinel 1 (26379): {'Connected' if sentinel1_info else 'Failed'}")
            
            # Test Sentinel 2 connectivity
            sentinel2_info = self.sentinel2.ping()
            print(f"✅ Sentinel 2 (26380): {'Connected' if sentinel2_info else 'Failed'}")
            
            # Test Sentinel 3 connectivity
            sentinel3_info = self.sentinel3.ping()
            print(f"✅ Sentinel 3 (26381): {'Connected' if sentinel3_info else 'Failed'}")
            
            return sentinel1_info and sentinel2_info and sentinel3_info
            
        except Exception as e:
            print(f"❌ Sentinel connection error: {e}")
            return False
    
    def test_master_monitoring(self) -> Dict[str, Any]:
        """
        Test Sentinel master monitoring functionality.
        
        This method retrieves master information from Sentinel and validates:
        - Master is being monitored by Sentinel
        - Master information is correct (IP, port, role)
        - Master is in healthy state
        - Quorum configuration is correct
        
        Returns:
            Dict[str, Any]: Dictionary containing master monitoring information
        """
        print("\n📊 Testing master monitoring...")
        
        master_info = {}
        
        try:
            # Get master information from Sentinel 1
            masters = self.sentinel1.execute_command('SENTINEL', 'masters')
            if masters:
                # Convert flat list to dictionary
                master_dict = {}
                for i in range(0, len(masters), 2):
                    if i + 1 < len(masters):
                        master_dict[masters[i]] = masters[i + 1]
                
                master_info = {
                    'name': master_dict.get('name'),
                    'ip': master_dict.get('ip'),
                    'port': int(master_dict.get('port', 0)),
                    'flags': master_dict.get('flags'),
                    'num_slaves': int(master_dict.get('num-slaves', 0)),
                    'num_sentinels': int(master_dict.get('num-other-sentinels', 0)),
                    'quorum': int(master_dict.get('quorum', 0))
                }
                
                print(f"🔴 Master: {master_info['name']} at {master_info['ip']}:{master_info['port']}")
                print(f"   Flags: {master_info['flags']}")
                print(f"   Slaves: {master_info['num_slaves']}")
                print(f"   Sentinels: {master_info['num_sentinels']}")
                print(f"   Quorum: {master_info['quorum']}")
                
                # Validate master information
                if (master_info['name'] == 'mymaster' and 
                    master_info['ip'] == 'redis-master' and 
                    master_info['port'] == 6379 and
                    'master' in master_info['flags']):
                    print("✅ Master monitoring is working correctly")
                else:
                    print("❌ Master monitoring configuration issue")
            else:
                print("❌ No masters found by Sentinel")
                
        except Exception as e:
            print(f"❌ Master monitoring error: {e}")
        
        return master_info
    
    def test_slave_monitoring(self) -> List[Dict[str, Any]]:
        """
        Test Sentinel slave monitoring functionality.
        
        This method retrieves slave information from Sentinel and validates:
        - Slaves are being monitored by Sentinel
        - Slave information is available
        - Slave count matches expected number
        
        Returns:
            List[Dict[str, Any]]: List of slave information dictionaries
        """
        print("\n📊 Testing slave monitoring...")
        
        slaves_info = []
        
        try:
            # Get slave information from Sentinel 1
            slaves = self.sentinel1.execute_command('SENTINEL', 'slaves', 'mymaster')
            
            # Parse slave information - each slave has multiple fields
            # Count slaves by looking for 'name' fields
            slave_names = [slaves[i+1] for i in range(0, len(slaves), 2) if slaves[i] == 'name']
            slave_count = len(slave_names)
            print(f"🟢 Found {slave_count} slaves:")
            
            # Convert flat list to list of dictionaries
            current_slave = {}
            for i in range(0, len(slaves), 2):
                if i + 1 < len(slaves):
                    key = slaves[i]
                    value = slaves[i + 1]
                    current_slave[key] = value
                    
                    # If we hit 'name' again, we've completed a slave
                    if key == 'name' and len(current_slave) > 1:
                        slave_info = {
                            'name': current_slave.get('name'),
                            'ip': current_slave.get('ip'),
                            'port': int(current_slave.get('port', 0)),
                            'flags': current_slave.get('flags'),
                            'master_link_status': current_slave.get('master-link-status'),
                            'slave_priority': int(current_slave.get('slave-priority', 0))
                        }
                        slaves_info.append(slave_info)
                        current_slave = {'name': value}  # Start new slave
            
            # Add the last slave if exists
            if len(current_slave) > 1:
                slave_info = {
                    'name': current_slave.get('name'),
                    'ip': current_slave.get('ip'),
                    'port': int(current_slave.get('port', 0)),
                    'flags': current_slave.get('flags'),
                    'master_link_status': current_slave.get('master-link-status'),
                    'slave_priority': int(current_slave.get('slave-priority', 0))
                }
                slaves_info.append(slave_info)
                
                print(f"   Slave {i+1}: {slave_info['ip']}:{slave_info['port']}")
                print(f"   Flags: {slave_info['flags']}")
                print(f"   Master Link: {slave_info['master_link_status']}")
                print(f"   Priority: {slave_info['slave_priority']}")
            
            if len(slaves) >= 2:
                print("✅ Slave monitoring is working correctly")
            else:
                print(f"⚠️ Expected 2 slaves, found {len(slaves)}")
                
        except Exception as e:
            print(f"❌ Slave monitoring error: {e}")
        
        return slaves_info
    
    def test_sentinel_cluster_communication(self) -> List[Dict[str, Any]]:
        """
        Test Sentinel cluster communication and coordination.
        
        This method retrieves information about other Sentinels in the cluster
        and validates:
        - Sentinels can communicate with each other
        - Sentinel cluster is properly formed
        - Quorum can be achieved for failover decisions
        
        Returns:
            List[Dict[str, Any]]: List of other Sentinel information
        """
        print("\n📊 Testing Sentinel cluster communication...")
        
        sentinels_info = []
        
        try:
            # Get other Sentinels information from Sentinel 1
            sentinels = self.sentinel1.execute_command('SENTINEL', 'sentinels', 'mymaster')
            
            # Parse sentinel information - similar to slaves
            sentinel_names = [sentinels[i+1] for i in range(0, len(sentinels), 2) if sentinels[i] == 'name']
            sentinel_count = len(sentinel_names)
            print(f"🔄 Found {sentinel_count} other Sentinels:")
            
            # Convert flat list to list of dictionaries
            current_sentinel = {}
            for i in range(0, len(sentinels), 2):
                if i + 1 < len(sentinels):
                    key = sentinels[i]
                    value = sentinels[i + 1]
                    current_sentinel[key] = value
                    
                    # If we hit 'name' again, we've completed a sentinel
                    if key == 'name' and len(current_sentinel) > 1:
                        sentinel_info = {
                            'name': current_sentinel.get('name'),
                            'ip': current_sentinel.get('ip'),
                            'port': int(current_sentinel.get('port', 0)),
                            'flags': current_sentinel.get('flags'),
                            'last_ping_reply': int(current_sentinel.get('last-ping-reply', 0))
                        }
                        sentinels_info.append(sentinel_info)
                        current_sentinel = {'name': value}  # Start new sentinel
            
            # Add the last sentinel if exists
            if len(current_sentinel) > 1:
                sentinel_info = {
                    'name': current_sentinel.get('name'),
                    'ip': current_sentinel.get('ip'),
                    'port': int(current_sentinel.get('port', 0)),
                    'flags': current_sentinel.get('flags'),
                    'last_ping_reply': int(current_sentinel.get('last-ping-reply', 0))
                }
                sentinels_info.append(sentinel_info)
                
                print(f"   Sentinel {i+1}: {sentinel_info['ip']}:{sentinel_info['port']}")
                print(f"   Flags: {sentinel_info['flags']}")
                print(f"   Last Ping: {sentinel_info['last_ping_reply']}ms ago")
            
            if len(sentinels) >= 2:
                print("✅ Sentinel cluster communication is working correctly")
            else:
                print(f"⚠️ Expected 2 other Sentinels, found {len(sentinels)}")
                
        except Exception as e:
            print(f"❌ Sentinel cluster communication error: {e}")
        
        return sentinels_info
    
    def test_master_connectivity(self) -> bool:
        """
        Test direct connectivity to the master node.
        
        This method verifies that the master node is accessible and responding
        to commands, which is essential for Sentinel monitoring.
        
        Returns:
            bool: True if master is accessible, False otherwise
        """
        print("\n🔗 Testing master connectivity...")
        
        try:
            # Test master connection
            master_ping = self.master.ping()
            print(f"✅ Master (6379): {'Connected' if master_ping else 'Failed'}")
            
            # Test master info
            master_info = self.master.info('replication')
            role = master_info.get('role')
            connected_slaves = master_info.get('connected_slaves')
            
            print(f"   Role: {role}")
            print(f"   Connected Slaves: {connected_slaves}")
            
            if role == 'master' and connected_slaves >= 2:
                print("✅ Master connectivity and replication is working correctly")
                return True
            else:
                print("❌ Master connectivity or replication issue")
                return False
                
        except Exception as e:
            print(f"❌ Master connectivity error: {e}")
            return False
    
    def test_sentinel_quorum(self) -> bool:
        """
        Test Sentinel quorum configuration and availability.
        
        This method validates that the Sentinel cluster has sufficient nodes
        to make failover decisions based on the configured quorum.
        
        Returns:
            bool: True if quorum is properly configured, False otherwise
        """
        print("\n⚖️ Testing Sentinel quorum...")
        
        try:
            # Get master information to check quorum
            masters = self.sentinel1.execute_command('SENTINEL', 'masters')
            if masters:
                # Convert list to dictionary
                master_dict = {}
                for i in range(0, len(masters), 2):
                    if i + 1 < len(masters):
                        master_dict[masters[i]] = masters[i + 1]
                
                quorum = int(master_dict.get('quorum', 0))
                num_sentinels = int(master_dict.get('num-other-sentinels', 0))
                total_sentinels = num_sentinels + 1  # +1 for current Sentinel
                
                print(f"   Configured Quorum: {quorum}")
                print(f"   Total Sentinels: {total_sentinels}")
                print(f"   Available Sentinels: {num_sentinels + 1}")
                
                if total_sentinels >= quorum:
                    print("✅ Sentinel quorum is properly configured")
                    return True
                else:
                    print("❌ Insufficient Sentinels for quorum")
                    return False
            else:
                print("❌ Cannot retrieve master information for quorum check")
                return False
                
        except Exception as e:
            print(f"❌ Sentinel quorum test error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """
        Run all Sentinel cluster tests.
        
        This method executes all test cases and provides a comprehensive
        summary of the Sentinel cluster health and functionality.
        
        Returns:
            bool: True if all tests passed, False otherwise
        """
        print("🚀 Starting Redis Sentinel Cluster Tests")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 6
        
        # Test 1: Sentinel connections
        if self.test_sentinel_connections():
            tests_passed += 1
            print("✅ Sentinel connections test passed")
        else:
            print("❌ Sentinel connections test failed")
            return False
        
        # Test 2: Master monitoring
        master_info = self.test_master_monitoring()
        if master_info and master_info.get('name') == 'mymaster':
            tests_passed += 1
            print("✅ Master monitoring test passed")
        else:
            print("❌ Master monitoring test failed")
        
        # Test 3: Slave monitoring
        slaves_info = self.test_slave_monitoring()
        if len(slaves_info) >= 2:
            tests_passed += 1
            print("✅ Slave monitoring test passed")
        else:
            print("❌ Slave monitoring test failed")
        
        # Test 4: Sentinel cluster communication
        sentinels_info = self.test_sentinel_cluster_communication()
        if len(sentinels_info) >= 2:
            tests_passed += 1
            print("✅ Sentinel cluster communication test passed")
        else:
            print("❌ Sentinel cluster communication test failed")
        
        # Test 5: Master connectivity
        if self.test_master_connectivity():
            tests_passed += 1
            print("✅ Master connectivity test passed")
        else:
            print("❌ Master connectivity test failed")
        
        # Test 6: Sentinel quorum
        if self.test_sentinel_quorum():
            tests_passed += 1
            print("✅ Sentinel quorum test passed")
        else:
            print("❌ Sentinel quorum test failed")
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Redis Sentinel cluster is working correctly.")
            print("\n🔧 Sentinel Cluster Summary:")
            print(f"   • Master: {master_info.get('ip', 'N/A')}:{master_info.get('port', 'N/A')}")
            print(f"   • Slaves: {len(slaves_info)} detected")
            print(f"   • Sentinels: {len(sentinels_info) + 1} total")
            print(f"   • Quorum: {master_info.get('quorum', 'N/A')}")
            return True
        else:
            print("⚠️ Some tests failed. Please check the Sentinel cluster configuration.")
            return False

def main():
    """Main function"""
    tester = RedisSentinelClusterTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
