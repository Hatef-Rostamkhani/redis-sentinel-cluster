#!/usr/bin/env python3
"""
Redis Sentinel Scenarios Test Script
===================================

This script tests various Redis Sentinel scenarios including:
1. Normal operation monitoring
2. Master failure simulation
3. Network partition scenarios
4. Sentinel failure scenarios
5. Recovery and failover testing

Usage:
    python3 test-sentinel-scenarios.py [scenario]

Scenarios:
    all        - Run all scenarios
    monitor    - Test normal monitoring
    failover   - Test master failover
    partition  - Test network partition
    recovery   - Test recovery scenarios
    stress     - Stress test scenarios
"""

import redis
import time
import sys
import subprocess
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class SentinelScenarioTester:
    """
    Comprehensive Redis Sentinel scenario testing class
    """
    
    def __init__(self):
        """Initialize connections to all Redis and Sentinel nodes"""
        self.master = redis.Redis(
            host='localhost', port=6379,
            password='redis_master_password_2024',
            decode_responses=True
        )
        
        self.replica1 = redis.Redis(
            host='localhost', port=6380,
            password='redis_replica_password_2024',
            decode_responses=True
        )
        
        self.replica2 = redis.Redis(
            host='localhost', port=6381,
            password='redis_replica_password_2024',
            decode_responses=True
        )
        
        self.sentinel1 = redis.Redis(
            host='localhost', port=26379,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        self.sentinel2 = redis.Redis(
            host='localhost', port=26380,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        self.sentinel3 = redis.Redis(
            host='localhost', port=26381,
            password='redis_sentinel_password_2024',
            decode_responses=True
        )
        
        self.test_data = {
            'scenario_test_key': 'Sentinel Test Data',
            'timestamp': datetime.now().isoformat(),
            'test_number': 1
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def check_cluster_health(self) -> Dict[str, Any]:
        """Check overall cluster health"""
        self.log("🔍 Checking cluster health...")
        
        health = {
            'master': False,
            'replicas': [],
            'sentinels': [],
            'replication': False,
            'sentinel_monitoring': False
        }
        
        try:
            # Check master
            master_ping = self.master.ping()
            master_info = self.master.info('replication')
            health['master'] = {
                'ping': master_ping,
                'role': master_info.get('role'),
                'connected_slaves': master_info.get('connected_slaves')
            }
            
            # Check replicas
            for i, replica in enumerate([self.replica1, self.replica2], 1):
                replica_ping = replica.ping()
                replica_info = replica.info('replication')
                health['replicas'].append({
                    'replica': i,
                    'ping': replica_ping,
                    'role': replica_info.get('role'),
                    'master_link_status': replica_info.get('master_link_status')
                })
            
            # Check sentinels
            for i, sentinel in enumerate([self.sentinel1, self.sentinel2, self.sentinel3], 1):
                sentinel_ping = sentinel.ping()
                try:
                    masters = sentinel.execute_command('SENTINEL', 'masters')
                    health['sentinels'].append({
                        'sentinel': i,
                        'ping': sentinel_ping,
                        'monitoring': len(masters) > 0 if masters else False
                    })
                except:
                    health['sentinels'].append({
                        'sentinel': i,
                        'ping': sentinel_ping,
                        'monitoring': False
                    })
            
            # Overall health
            health['replication'] = (
                health['master']['role'] == 'master' and
                health['master']['connected_slaves'] >= 2 and
                all(r['master_link_status'] == 'up' for r in health['replicas'])
            )
            
            health['sentinel_monitoring'] = (
                len(health['sentinels']) >= 3 and
                all(s['ping'] for s in health['sentinels']) and
                sum(1 for s in health['sentinels'] if s['monitoring']) >= 2
            )
            
        except Exception as e:
            self.log(f"Health check error: {e}", "ERROR")
        
        return health
    
    def test_normal_monitoring(self) -> bool:
        """Test normal Sentinel monitoring operation"""
        self.log("📊 Testing normal monitoring scenario...")
        
        try:
            # Write test data
            self.master.set('monitor_test', json.dumps(self.test_data))
            time.sleep(2)
            
            # Check replication
            replica1_data = self.replica1.get('monitor_test')
            replica2_data = self.replica2.get('monitor_test')
            
            if replica1_data == replica2_data == json.dumps(self.test_data):
                self.log("✅ Normal monitoring: Data replicated successfully")
                return True
            else:
                self.log("❌ Normal monitoring: Data replication failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Normal monitoring error: {e}", "ERROR")
            return False
    
    def test_master_failure(self) -> bool:
        """Test master failure and failover scenario"""
        self.log("💥 Testing master failure scenario...")
        
        try:
            # Write data before failure
            self.master.set('failover_test', 'Before failure')
            time.sleep(1)
            
            # Temporarily disable restart policy to prevent auto-restart
            self.log("🛑 Stopping master container...")
            subprocess.run(['docker', 'update', '--restart=no', 'redis-master'], check=True)
            subprocess.run(['docker', 'stop', 'redis-master'], check=True)
            time.sleep(5)
            
            # Check Sentinel detection
            masters = self.sentinel1.execute_command('SENTINEL', 'masters')
            if masters:
                master_dict = {}
                for i in range(0, len(masters), 2):
                    if i + 1 < len(masters):
                        master_dict[masters[i]] = masters[i + 1]
                
                if 's_down' in master_dict.get('flags', ''):
                    self.log("✅ Master failure: Sentinel detected master as down")
                else:
                    self.log("⚠️ Master failure: Sentinel not yet detected failure")
            
            # Wait for failover
            self.log("⏳ Waiting for failover...")
            time.sleep(15)
            
            # Check if failover occurred
            try:
                new_master_addr = self.sentinel1.execute_command('SENTINEL', 'get-master-addr-by-name', 'mymaster')
                if new_master_addr:
                    self.log(f"✅ Failover detected: New master at {new_master_addr[0]}:{new_master_addr[1]}")
                    
                    # Test new master - accept any replica as valid failover
                    if new_master_addr[0] in ['redis-replica-1', 'redis-replica-2']:
                        # Determine which replica is now the master
                        if new_master_addr[0] == 'redis-replica-1':
                            new_master = self.replica1
                        else:
                            new_master = self.replica2
                        
                        # Test write to new master
                        new_master.set('failover_test', 'After failover')
                        self.log("✅ Failover: New master accepts writes")
                        
                        # Restore restart policy and restart original master as replica
                        self.log("🔄 Restarting original master as replica...")
                        subprocess.run(['docker', 'update', '--restart=unless-stopped', 'redis-master'], check=True)
                        subprocess.run(['docker', 'start', 'redis-master'], check=True)
                        time.sleep(10)
                        
                        return True
                    else:
                        self.log(f"⚠️ Failover: Master is {new_master_addr[0]} (may be original master restarted)")
                        # Restore restart policy
                        subprocess.run(['docker', 'update', '--restart=unless-stopped', 'redis-master'], check=True)
                        subprocess.run(['docker', 'start', 'redis-master'], check=True)
                        return False
                else:
                    self.log("❌ Failover: No new master detected")
                    # Restore restart policy
                    subprocess.run(['docker', 'update', '--restart=unless-stopped', 'redis-master'], check=True)
                    subprocess.run(['docker', 'start', 'redis-master'], check=True)
                    return False
                    
            except Exception as e:
                self.log(f"❌ Failover error: {e}", "ERROR")
                # Restore restart policy
                subprocess.run(['docker', 'update', '--restart=unless-stopped', 'redis-master'], check=True)
                subprocess.run(['docker', 'start', 'redis-master'], check=True)
                return False
                
        except Exception as e:
            self.log(f"❌ Master failure test error: {e}", "ERROR")
            # Restore restart policy
            subprocess.run(['docker', 'update', '--restart=unless-stopped', 'redis-master'], check=True)
            subprocess.run(['docker', 'start', 'redis-master'], check=True)
            return False
    
    def test_network_partition(self) -> bool:
        """Test network partition scenario"""
        self.log("🌐 Testing network partition scenario...")
        
        try:
            # Write data before partition
            self.master.set('partition_test', 'Before partition')
            time.sleep(1)
            
            # Simulate network partition by stopping one Sentinel
            self.log("🛑 Stopping Sentinel 1 to simulate partition...")
            subprocess.run(['docker', 'stop', 'redis-sentinel-1'], check=True)
            time.sleep(5)
            
            # Check remaining Sentinels
            sentinel2_ping = self.sentinel2.ping()
            sentinel3_ping = self.sentinel3.ping()
            
            if sentinel2_ping and sentinel3_ping:
                self.log("✅ Network partition: Remaining Sentinels are healthy")
                
                # Check if quorum is maintained
                masters = self.sentinel2.execute_command('SENTINEL', 'masters')
                if masters:
                    master_dict = {}
                    for i in range(0, len(masters), 2):
                        if i + 1 < len(masters):
                            master_dict[masters[i]] = masters[i + 1]
                    
                    quorum = int(master_dict.get('quorum', 0))
                    num_sentinels = int(master_dict.get('num-other-sentinels', 0))
                    
                    if num_sentinels >= quorum:
                        self.log("✅ Network partition: Quorum maintained")
                        # Restart the stopped Sentinel
                        self.log("🔄 Restarting Sentinel 1...")
                        subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
                        time.sleep(5)
                        return True
                    else:
                        self.log("❌ Network partition: Quorum lost")
                        # Restart the stopped Sentinel
                        subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
                        return False
                else:
                    self.log("❌ Network partition: No master information")
                    # Restart the stopped Sentinel
                    subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
                    return False
            else:
                self.log("❌ Network partition: Remaining Sentinels unhealthy")
                # Restart the stopped Sentinel
                subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
                return False
                
        except Exception as e:
            self.log(f"❌ Network partition test error: {e}", "ERROR")
            # Restart the stopped Sentinel
            subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
            return False
    
    def test_sentinel_failure(self) -> bool:
        """Test Sentinel failure scenarios"""
        self.log("🔧 Testing Sentinel failure scenario...")
        
        try:
            # Check initial state
            initial_health = self.check_cluster_health()
            if not initial_health['sentinel_monitoring']:
                self.log("❌ Sentinel failure: Initial state unhealthy")
                return False
            
            # Stop one Sentinel
            self.log("🛑 Stopping Sentinel 2...")
            subprocess.run(['docker', 'stop', 'redis-sentinel-2'], check=True)
            time.sleep(5)
            
            # Check remaining Sentinels
            sentinel1_ping = self.sentinel1.ping()
            sentinel3_ping = self.sentinel3.ping()
            
            if sentinel1_ping and sentinel3_ping:
                self.log("✅ Sentinel failure: Remaining Sentinels operational")
                
                # Check if monitoring continues
                masters = self.sentinel1.execute_command('SENTINEL', 'masters')
                if masters:
                    self.log("✅ Sentinel failure: Monitoring continues")
                    # Restart the stopped Sentinel
                    self.log("🔄 Restarting Sentinel 2...")
                    subprocess.run(['docker', 'start', 'redis-sentinel-2'], check=True)
                    time.sleep(5)
                    return True
                else:
                    self.log("❌ Sentinel failure: Monitoring lost")
                    # Restart the stopped Sentinel
                    subprocess.run(['docker', 'start', 'redis-sentinel-2'], check=True)
                    return False
            else:
                self.log("❌ Sentinel failure: Remaining Sentinels failed")
                # Restart the stopped Sentinel
                subprocess.run(['docker', 'start', 'redis-sentinel-2'], check=True)
                return False
                
        except Exception as e:
            self.log(f"❌ Sentinel failure test error: {e}", "ERROR")
            # Restart the stopped Sentinel
            subprocess.run(['docker', 'start', 'redis-sentinel-2'], check=True)
            return False
    
    def test_recovery_scenario(self) -> bool:
        """Test recovery after failures"""
        self.log("🔄 Testing recovery scenario...")
        
        try:
            # Restart stopped services
            self.log("🔄 Restarting stopped services...")
            
            # Restart master if stopped
            result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=redis-master'], 
                                  capture_output=True, text=True)
            if not result.stdout.strip():
                subprocess.run(['docker', 'start', 'redis-master'], check=True)
                self.log("✅ Recovery: Master restarted")
            
            # Restart Sentinel 1 if stopped
            result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=redis-sentinel-1'], 
                                  capture_output=True, text=True)
            if not result.stdout.strip():
                subprocess.run(['docker', 'start', 'redis-sentinel-1'], check=True)
                self.log("✅ Recovery: Sentinel 1 restarted")
            
            # Restart Sentinel 2 if stopped
            result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=redis-sentinel-2'], 
                                  capture_output=True, text=True)
            if not result.stdout.strip():
                subprocess.run(['docker', 'start', 'redis-sentinel-2'], check=True)
                self.log("✅ Recovery: Sentinel 2 restarted")
            
            # Wait for services to stabilize
            self.log("⏳ Waiting for services to stabilize...")
            time.sleep(20)
            
            # Check final health
            final_health = self.check_cluster_health()
            
            if (final_health['master']['ping'] and 
                len(final_health['replicas']) >= 2 and
                len(final_health['sentinels']) >= 3):
                self.log("✅ Recovery: Cluster fully recovered")
                return True
            else:
                self.log("❌ Recovery: Cluster not fully recovered")
                return False
                
        except Exception as e:
            self.log(f"❌ Recovery test error: {e}", "ERROR")
            return False
    
    def test_stress_scenario(self) -> bool:
        """Test stress scenarios with multiple operations"""
        self.log("⚡ Testing stress scenario...")
        
        try:
            # Perform multiple operations
            operations = []
            for i in range(10):
                key = f'stress_test_{i}'
                value = f'Stress test data {i} - {datetime.now().isoformat()}'
                
                # Write to master
                self.master.set(key, value)
                operations.append((key, value))
                
                # Small delay
                time.sleep(0.5)
            
            # Wait for replication
            time.sleep(5)
            
            # Verify all operations
            success_count = 0
            for key, expected_value in operations:
                replica1_value = self.replica1.get(key)
                replica2_value = self.replica2.get(key)
                
                if replica1_value == replica2_value == expected_value:
                    success_count += 1
            
            success_rate = (success_count / len(operations)) * 100
            self.log(f"✅ Stress test: {success_count}/{len(operations)} operations successful ({success_rate:.1f}%)")
            
            return success_rate >= 80  # 80% success rate threshold
            
        except Exception as e:
            self.log(f"❌ Stress test error: {e}", "ERROR")
            return False
    
    def run_scenario(self, scenario: str) -> bool:
        """Run a specific scenario"""
        self.log(f"🚀 Starting scenario: {scenario}")
        
        scenarios = {
            'monitor': self.test_normal_monitoring,
            'failover': self.test_master_failure,
            'partition': self.test_network_partition,
            'recovery': self.test_recovery_scenario,
            'stress': self.test_stress_scenario
        }
        
        if scenario in scenarios:
            return scenarios[scenario]()
        else:
            self.log(f"❌ Unknown scenario: {scenario}", "ERROR")
            return False
    
    def run_all_scenarios(self) -> Dict[str, bool]:
        """Run all scenarios"""
        self.log("🎯 Running all Sentinel scenarios...")
        
        results = {}
        scenarios = ['monitor', 'failover', 'partition', 'recovery', 'stress']
        
        for scenario in scenarios:
            self.log(f"\n{'='*50}")
            self.log(f"Running scenario: {scenario}")
            self.log('='*50)
            
            try:
                results[scenario] = self.run_scenario(scenario)
                
                if results[scenario]:
                    self.log(f"✅ Scenario '{scenario}' PASSED")
                else:
                    self.log(f"❌ Scenario '{scenario}' FAILED")
                    
            except Exception as e:
                self.log(f"❌ Scenario '{scenario}' ERROR: {e}", "ERROR")
                results[scenario] = False
            
            # Wait between scenarios
            time.sleep(5)
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test results summary"""
        self.log("\n" + "="*60)
        self.log("📊 SENTINEL SCENARIOS TEST SUMMARY")
        self.log("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for scenario, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{scenario.upper():<15}: {status}")
        
        self.log("-"*60)
        self.log(f"TOTAL RESULTS: {passed}/{total} scenarios passed")
        
        if passed == total:
            self.log("🎉 ALL SCENARIOS PASSED! Sentinel cluster is working perfectly.")
        else:
            self.log("⚠️ Some scenarios failed. Check the cluster configuration.")
        
        self.log("="*60)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 test-sentinel-scenarios.py [scenario]")
        print("Scenarios: all, monitor, failover, partition, recovery, stress")
        sys.exit(1)
    
    scenario = sys.argv[1].lower()
    tester = SentinelScenarioTester()
    
    try:
        if scenario == 'all':
            results = tester.run_all_scenarios()
            tester.print_summary(results)
            success = all(results.values())
        else:
            success = tester.run_scenario(scenario)
            if success:
                print(f"✅ Scenario '{scenario}' PASSED")
            else:
                print(f"❌ Scenario '{scenario}' FAILED")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
