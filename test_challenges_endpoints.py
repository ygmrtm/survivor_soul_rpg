#!/usr/bin/env python3

"""
Test script to verify that the new challenge endpoints are working correctly.
This script tests each individual challenge endpoint to ensure they respond properly.
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api/adventure"

def test_endpoint(endpoint, method="POST", data=None, params=None):
    """Test a single endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "POST":
            response = requests.post(url, json=data, params=params)
        else:
            response = requests.get(url, params=params)

        print(f"Testing {method} {endpoint} - Status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success: {json.dumps(result, indent=2)}")
                return True, result
            except json.JSONDecodeError:
                print(f"❌ Error: Invalid JSON response")
                return False, None
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, None

def main():
    print("🧪 Testing Challenge Endpoints")
    print("=" * 50)

    # Get current week and year
    current_date = datetime.now()
    week_number = current_date.isocalendar()[1]
    year_number = current_date.year

    print(f"Current Week: {week_number}, Year: {year_number}")

    # Test individual challenge endpoints
    endpoints_to_test = [
        f"/challenges/consecutive/{week_number}/{year_number}",
        f"/challenges/habits/{week_number}/{year_number}",
        f"/challenges/habit_longest_streak_created/{week_number}/{year_number}",
        "/challenges/habit_longest_streak_executed",
        f"/challenges/coding/{week_number}/{year_number}",
        f"/challenges/bike/{week_number}/{year_number}",
        f"/challenges/stencil/{week_number}/{year_number}",
        f"/challenges/epics/{week_number}/{year_number}",
        f"/challenges/expired/{week_number}/{year_number}",
        "/challenges/due_soon/21"
    ]

    passed_tests = 0
    total_tests = len(endpoints_to_test)

    for endpoint in endpoints_to_test:
        success, _ = test_endpoint(endpoint)
        if success:
            passed_tests += 1
        print("-" * 30)

    print(f"\n📊 Test Results: {passed_tests}/{total_tests} endpoints passed")

    if passed_tests == total_tests:
        print("🎉 All endpoints are working correctly!")
    else:
        print("⚠️ Some endpoints failed. Check the error messages above.")

if __name__ == "__main__":
    main()