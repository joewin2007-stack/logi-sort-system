from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel

# 1. Initialize the core network web application gateway
app = FastAPI(title="Logi-Sort Production API Gateway - Day 8")

# 2. Database Connection Helper Function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_mysql_password",  # Replace with your actual password
        database="logi_sort"            # Replace with your database name
    )

# 3. Create a strict data validation schema for incoming telemetry
class TripPayload(BaseModel):
    driver_id: int
    distance_km: float
    traffic_density: float

# 4. System Health Endpoint
@app.get("/api/v1/health")
def check_health():
    return {"status": "healthy", "milestone": "Day 8 Project Target Locked"}

# 5. The Core Integration Route (Connecting API parameters directly to SQL query executions)
@app.post("/api/v1/trips/verify")
def verify_and_log_trip(payload: TripPayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Concept Link to your 12:00 PM SQL class: Implicit validation via checking structural records
        # Check if the incoming driver payload matches an actual record in your database
        driver_query = "SELECT * FROM drivers WHERE driver_id = %s"
        cursor.execute(driver_query, (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            # If driver isn't found, stop execution immediately and alert the client application
            raise HTTPException(status_code=404, detail="Driver validation failed. ID not found.")
        
        # Return a clean JSON validation payload back to your frontend system
        return {
            "status": "synchronized",
            "message": "Telemetry matched against active database tables.",
            "data": {
                "driver_name": driver_record.get("name", "Active Operator"),
                "assigned_distance": payload.distance_km,
                "traffic_coefficient": payload.traffic_density
            }
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection pipeline error: {str(err)}")
    
    finally:
        # Crucial clean-up steps so your local server doesn't memory-leak or run out of database slots
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()