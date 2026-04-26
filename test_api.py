"""
test_api.py — Test Suite for Trading AI Framework API
=====================================================

Run automated tests to verify API endpoints are working correctly.

Usage:
    python test_api.py

Requirements:
    pip install requests pytest

Author: Framework Team
License: MIT
"""

import requests
import json
import time
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:5000"

class TestAPI:
    """Test suite for Trading AI Framework API"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []

    def test_health(self) -> bool:
        """Test health check endpoint"""
        print("\n🔍 Testing: GET /health")
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data['status'] == 'healthy', "Health status should be 'healthy'"
            print(f"✅ PASS: {data['message']}")
            return True
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return False

    def test_simulation_info(self) -> bool:
        """Test simulation info endpoint"""
        print("\n🔍 Testing: GET /simulation-info")
        try:
            response = requests.get(f"{self.base_url}/simulation-info")
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert 'algorithms' in data, "Response should contain 'algorithms'"
            assert len(data['algorithms']) == 6, "Should have 6 algorithms"
            print(f"✅ PASS: Found {len(data['algorithms'])} algorithms")
            print(f"  Algorithms: {', '.join([a['name'] for a in data['algorithms']])}")
            return True
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return False

    def test_run_simulation(self, **params) -> bool:
        """Test simulation run endpoint"""
        print("\n🔍 Testing: GET /run-simulation")
        print(f"  Parameters: {params}")
        try:
            response = requests.get(
                f"{self.base_url}/run-simulation",
                params=params,
                timeout=300  # 5 minute timeout
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            # Validate response structure
            assert data['status'] == 'success', f"Status should be 'success', got {data['status']}"
            assert 'results' in data, "Response should contain 'results'"
            assert 'summary' in data, "Response should contain 'summary'"
            assert len(data['results']) == 6, f"Should have 6 results, got {len(data['results'])}"
            
            # Validate result structure
            for result in data['results']:
                assert 'name' in result, "Result should have 'name'"
                assert 'final_value' in result, "Result should have 'final_value'"
                assert 'profit' in result, "Result should have 'profit'"
                assert 'execution_time' in result, "Result should have 'execution_time'"
                assert 'states_explored' in result, "Result should have 'states_explored'"
                assert 'peak_memory' in result, "Result should have 'peak_memory'"
            
            # Validate summary
            summary = data['summary']
            assert summary['total_algorithms'] == 6, "Summary should have total_algorithms"
            assert 'best_algorithm' in summary, "Summary should have 'best_algorithm'"
            assert 'best_profit' in summary, "Summary should have 'best_profit'"
            
            print(f"✅ PASS: Simulation completed successfully")
            print(f"  Total Algorithms: {summary['total_algorithms']}")
            print(f"  Best Algorithm: {summary['best_algorithm']}")
            print(f"  Best Profit: ${summary['best_profit']:.2f}")
            print(f"  Average Time: {summary['average_execution_time']:.4f}s")
            
            # Print all results
            print(f"\n  Algorithm Results:")
            for result in data['results']:
                print(f"    {result['name']:<15} | Profit: ${result['profit']:>10.2f} | "
                      f"Time: {result['execution_time']:>8.4f}s | "
                      f"States: {result['states_explored']:>6} | "
                      f"Memory: {result['peak_memory']:>8.2f}KB")
            
            return True
        except requests.exceptions.Timeout:
            print(f"❌ FAIL: Request timeout (simulation took too long)")
            return False
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return False

    def test_invalid_data_file(self) -> bool:
        """Test error handling for invalid data file"""
        print("\n🔍 Testing: GET /run-simulation with invalid data file")
        try:
            response = requests.get(
                f"{self.base_url}/run-simulation",
                params={'data': 'nonexistent.csv'}
            )
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            data = response.json()
            assert data['status'] == 'error', "Status should be 'error'"
            print(f"✅ PASS: Error handling works correctly")
            print(f"  Error: {data['message']}")
            return True
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return False

    def test_custom_parameters(self) -> bool:
        """Test simulation with custom parameters"""
        print("\n🔍 Testing: GET /run-simulation with custom parameters")
        params = {
            'cash': 5000,
            'minimax_depth': 3,
            'ao_depth': 3
        }
        print(f"  Parameters: {params}")
        try:
            response = requests.get(
                f"{self.base_url}/run-simulation",
                params=params,
                timeout=300
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data['status'] == 'success', "Status should be 'success'"
            assert data['summary']['starting_capital'] == 5000, "Starting capital should be 5000"
            print(f"✅ PASS: Custom parameters accepted")
            print(f"  Starting Capital: ${data['summary']['starting_capital']}")
            return True
        except Exception as e:
            print(f"❌ FAIL: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("\n" + "="*60)
        print("🧪 TRADING AI FRAMEWORK - API TEST SUITE")
        print("="*60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Simulation Info", self.test_simulation_info),
            ("Invalid Data File", self.test_invalid_data_file),
            ("Custom Parameters", self.test_custom_parameters),
            ("Run Simulation", lambda: self.test_run_simulation(
                data='data/sample_prices.csv',
                cash=10000
            )),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {str(e)}")
                failed += 1
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {passed}/{len(tests)}")
        print(f"❌ Failed: {failed}/{len(tests)}")
        print("="*60)
        
        return {
            'total': len(tests),
            'passed': passed,
            'failed': failed,
            'success': failed == 0
        }


if __name__ == '__main__':
    import sys
    
    print("\n⏳ Waiting for API to be ready...")
    
    # Wait for API to be available
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✅ API is ready!\n")
            break
        except:
            if attempt < max_attempts - 1:
                print(f"  Attempt {attempt + 1}/{max_attempts}: Waiting for API...")
                time.sleep(1)
            else:
                print(f"❌ API is not responding at {BASE_URL}")
                print("   Make sure the Flask backend is running:")
                print("   python api.py")
                sys.exit(1)
    
    # Run tests
    tester = TestAPI(BASE_URL)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)
