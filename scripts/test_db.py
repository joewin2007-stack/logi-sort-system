import sys
import os

# Appending the workspace path to system variables to handle native directory execution smoothly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from scripts.database import get_db_connection, initialize_database_schemas

def run_system_database_tests():
    """Runs an end-to-end integration and sanity test against our local MySQL layer."""
    print("🧪 Day 15: Commencing Automated Database Architecture Verification Suite...\n" + "="*80)
    
    # TEST 1: Database Connection Integrity
    print("▶️ TEST 1: Checking Warehouse Channel Connection...")
    try:
        connection = get_db_connection()
        if connection.is_connected():
            print("✅ PASS: Database link verified and active.")
            connection.close()
    except Exception as e:
        print(f"❌ FAIL: Connection channel dropped out. Reason: {str(e)}")
        sys.exit(1)

    # TEST 2: Schema Self-Healing Capabilities
    print("\n▶️ TEST 2: Verifying Self-Healing Infrastructure Initialization...")
    try:
        initialize_database_schemas()
        print("✅ PASS: Schema configurations evaluated and seeded seamlessly.")
    except Exception as e:
        print(f"❌ FAIL: Relational table initialization hit an exception: {str(e)}")
        sys.exit(1)

    # TEST 3: End-to-End Relational Data Transaction Loops
    print("\n▶️ TEST 3: Executing Live Persistence and Relational Read Verification...")
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Insert a sample test-run log entry directly into the database
        print("  - Running simulation write-back into 'trips' table...")
        insert_query = """
            INSERT INTO trips (driver_id, distance_km, traffic_density, predicted_duration_minutes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (1, 25.5, 0.35, 45.2))
        connection.commit()
        test_trip_id = cursor.lastrowid
        print(f"  - Record added safely. Assigned Log ID: {test_trip_id}")
        
        # Execute a lookup with a relational LEFT JOIN to pull back the driver name
        print("  - Validating cross-table JOIN execution matching records...")
        select_query = """
            SELECT t.trip_id, t.distance_km, d.name AS driver_name 
            FROM trips t
            LEFT JOIN drivers d ON t.driver_id = d.driver_id
            WHERE t.trip_id = %s
        """
        cursor.execute(select_query, (test_trip_id,))
        result = cursor.fetchone()
        
        if result and result['driver_name'] == "Alex Johnson":
            print(f"  - Retrieved Telemetry Data -> Trip ID: {result['trip_id']} | Driver: {result['driver_name']}")
            print("✅ PASS: Persistent write-back and relational data JOINs are completely stable.")
        else:
            print("❌ FAIL: Retrieved transaction properties do not match structural expectations.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ FAIL: Transaction validation block failed with error: {str(e)}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
    print("\n" + "="*80 + "\n🎉 SUCCESS: All 3 Database Verification Framework Tests Passed Unconditionally!")

if __name__ == "__main__":
    run_system_database_tests()