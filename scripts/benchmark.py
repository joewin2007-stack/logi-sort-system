import requests
import time
import concurrent.futures
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1/trips/verify"
TOTAL_REQUESTS = 50  # Total simulated truck driver requests
CONCURRENT_WORKERS = 5 # Number of simultaneous parallel network threads

def send_benchmark_payload(request_index):
    """Fires a single payload request and measures its direct turnaround latency."""
    payload = {
        "driver_id": 1,
        "distance_km": 10.0 + (request_index * 0.5), # Varying inputs to simulate real usage
        "traffic_density": 0.2 + ((request_index % 5) * 0.1)
    }
    
    start = time.time()
    try:
        response = requests.post(BASE_URL, json=payload, timeout=5)
        duration = (time.time() - start) * 1000
        return response.status_code, duration
    except Exception as e:
        return "ERROR", 0.0

def run_load_benchmark():
    print(f"🧪 Day 19: Commencing System Load Benchmarking...")
    print(f"⚡ Stress Parameters: Sending {TOTAL_REQUESTS} requests via {CONCURRENT_WORKERS} parallel workers.\n" + "="*80)
    
    # Verify the server is running before kicking off threads
    try:
        requests.get("http://127.0.0.1:8000/api/v1/health")
    except:
        print("❌ CRITICAL: API server is offline! Start Uvicorn before running this benchmark.")
        sys.exit(1)
        
    start_suite_time = time.time()
    success_count = 0
    failure_count = 0
    latencies = []

    # Using thread pooling to smash the API concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        # Map our payload calls across multiple background threads
        futures = [executor.submit(send_benchmark_payload, i) for i in range(TOTAL_REQUESTS)]
        
        for index, future in enumerate(concurrent.futures.as_completed(futures)):
            status, latency = future.result()
            if status == 200:
                success_count += 1
                latencies.append(latency)
            else:
                failure_count += 1
                
            if (index + 1) % 10 == 0:
                print(f" 📦 Processed {index + 1}/{TOTAL_REQUESTS} requests...")

    total_suite_duration = time.time() - start_suite_time
    throughput = TOTAL_REQUESTS / total_suite_duration

    # Calculate performance matrix
    print("="*80 + "\n📊 BENCHMARK PERFORMANCE METRICS SUMMARY:")
    print(f" ✅ Successful Requests : {success_count}/{TOTAL_REQUESTS}")
    print(f" ❌ Failed Requests     : {failure_count}")
    print(f" ⏱️  Total Elapsed Time  : {total_suite_duration:.2f} seconds")
    print(f" 🚀 System Throughput   : {throughput:.2f} requests/second")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        print(f" 📉 Average Network Latency : {avg_latency:.2f}ms")
        print(f" 📈 Peak/Max Request Latency: {max_latency:.2f}ms")
        print(f" 🎯 Fastest Request Latency : {min_latency:.2f}ms")
    print("="*80 + "\n🎉 SUCCESS: System benchmark test complete under multi-threaded payload environments!")

if __name__ == "__main__":
    run_load_benchmark()