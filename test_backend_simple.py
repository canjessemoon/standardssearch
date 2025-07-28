#!/usr/bin/env python3
"""
Simple test script to validate the backend search functionality
"""
import requests
import json
import sys

def test_search(query, expected_max_results=None):
    """Test a search query and return results"""
    url = "http://localhost:5000/search"
    payload = {
        "query": query,
        "language": "en"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Search for '{query}':")
            print(f"  Total matches: {data.get('total_matches', 0)}")
            
            if expected_max_results and data.get('total_matches', 0) > expected_max_results:
                print(f"  ⚠ WARNING: Too many matches (expected ≤ {expected_max_results})")
            
            # Show first few results
            results = data.get('results', [])
            for i, result in enumerate(results[:3]):
                print(f"  Result {i+1}: Page {result.get('page', 'N/A')}, Context: {result.get('context', '')[:100]}...")
            
            return data
        else:
            print(f"✗ Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("✗ Error: Cannot connect to backend server")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_server_health():
    """Test if the server is responding"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"Server health check: {response.status_code}")
        return response.status_code == 200
    except:
        print("Server health check: Failed")
        return False

if __name__ == "__main__":
    print("=== Backend Search Test ===")
    
    # Test server health
    if not test_server_health():
        print("Backend server is not responding. Please start it first.")
        sys.exit(1)
    
    # Test the problematic search term
    print("\n1. Testing 'accidental activation' (should have reasonable number of matches):")
    result1 = test_search("accidental activation", expected_max_results=50)
    
    # Test a simple search
    print("\n2. Testing 'head clearance':")
    result2 = test_search("head clearance")
    
    # Test exact phrase
    print("\n3. Testing exact phrase 'emergency procedures':")
    result3 = test_search("emergency procedures")
    
    print("\n=== Test Complete ===")
