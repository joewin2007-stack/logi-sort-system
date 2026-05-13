import mysql.connector
import random
import time

# 1. Database Connection Configuration
config = {
    'user': 'root',
    'password': '', 
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'logi_sort',
    'use_pure': True  # This helps bypass some C-extension driver issues
}

try:
    # 2. Establish Connection
    print("Connecting to MySQL...")
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    # 3. Generate 5,000 Synthetic Trip Records
    print("Generating 5,000 logistics records...")
    data = []
    for _ in range(5000):
        dist = round(random.uniform(5, 150), 2)       # Distance in KM
        traffic = random.randint(1, 10)               # 1 = Smooth, 10 = Jam
        weather = round(random.uniform(1.0, 2.0), 1)  # 1.0 = Clear, 2.0 = Stormy
        day = random.randint(0, 6)                    # 0=Mon, 6=Sun
        hour = random.randint(0, 23)                  # 24-hour format
        
        # ML Logic: Base speed + Distance factor + Traffic delay + Weather delay + Noise
        # This creates a "pattern" for our ML model to learn later
        base_time = 10 
        calc_time = base_time + (dist * 1.2) + (traffic * 5.5) + (weather * 15) + random.uniform(-10, 10)
        
        data.append((dist, traffic, weather, day, hour, round(calc_time, 2)))

    # 4. Bulk Insert (Much faster than one-by-one)
    query = """
        INSERT INTO trip_logs 
        (distance_km, traffic_density, weather_impact, day_of_week, hour_of_day, actual_time_mins) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    cursor.executemany(query, data)
    db.commit()

    print(f"✅ Success! {cursor.rowcount} rows injected into 'trip_logs' table.")

except mysql.connector.Error as err:
    print(f"❌ MySQL Error: {err}")
finally:
    if 'db' in locals() and db.is_connected():
        cursor.close()
        db.close()
        print("Connection closed.")