import requests
import sys

# The base URL where your local Uvicorn development server runs
BASE_URL = "http://127.0.0.1:8000"

def run_api_integration_tests():
    print("🧪 Day 16: Commencing Automated API Gateway Verification Suite...\n" + "="*80)
    
    # TEST 1: Verify the Health Check Endpoint
    print("▶️ TEST 1: Pinging /api/v1/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  - Server Response: {data['status']} | Milestone: {data['milestone']}")
            print("✅ PASS: Health gateway is fully operational.")
        else:
            print(f"❌ FAIL: Expected HTTP 200, but got {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to server. Did you forget to start Uvicorn?")
        sys.exit(1)

    # TEST 2: Verify a Successful Trip Prediction (Driver ID: 1)
    print("\n▶️ TEST 2: Testing Valid Post Payload (Driver 1)...")
    payload_success = {
        "driver_id": 1,
        "distance_km": 15.5,
        "traffic_density": 0.4
    }
    response = requests.post(f"{BASE_URL}/api/v1/trips/verify", json=payload_success)
    if response.status_code == 200:
        data = response.json()
        print(f"  - Driver Matched: {data['routing_metadata']['driver_name']}")
        print(f"  - Predicted Duration: {data['predictive_analytics']['estimated_duration_minutes']} mins")
        print(f"  - Assigned Log ID: {data['logged_trip_id']}")
        print("✅ PASS: Telemetry processed, predicted, and written to DB perfectly.")
    else:
        print(f"❌ FAIL: Expected HTTP 200, but got {response.status_code}. Response: {response.text}")
        sys.exit(1)

    # TEST 3: Verify Security Constraints (Negative Distance Check)
    print("\n▶️ TEST 3: Testing Input Boundary Security (Negative Distance Check)...")
    payload_bad_dist = {
        "driver_id": 1,
        "distance_km": -5.0,  # This should spark a validation flag
        "traffic_density": 0.2
    }
    response = requests.post(f"{BASE_URL}/api/v1/trips/verify", json=payload_bad_dist)
    if response.status_code == 422:  # 422 is FastAPI's standard data validation error code
        print("  - Server blocked the request as expected.")
        print("✅ PASS: Input security guards intercepted the negative distance payload.")
    else:
        print(f"❌ FAIL: Expected HTTP 422 Validation Error, but got {response.status_code}")
        sys.exit(1)

    # TEST 4: Verify Missing Driver Handling (Driver ID: 9999)
    print("\n▶️ TEST 4: Testing Unknown Entity Handling (Driver 9999)...")
    payload_bad_driver = {
        "driver_id": 9999,  # This driver doesn't exist
        "distance_km": 10.0,
        "traffic_density": 0.1
    }
    response = requests.post(f"{BASE_URL}/api/v1/trips/verify", json=payload_bad_driver)
    if response.status_code == 404:
        print("  - Server cleanly rejected the request with an explicit 404.")
        print("✅ PASS: Database checking layer caught the fake identity parameter safely.")
    else:
        print(f"❌ FAIL: Expected HTTP 404 Not Found, but got {response.status_code}")
        sys.exit(1)

    print("\n" + "="*80 + "\n🎉 SUCCESS: All 4 API Gateway Infrastructure Tests Passed Unconditionally!")

if __name__ == "__main__":
    run_api_integration_tests()