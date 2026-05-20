from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Logi-Sort Production API Gateway - Day 10")

# Centralized database configuration management
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",  # Replace with your actual password
    "database": "logi_sort"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class TripPayload(BaseModel):
    driver_id: int = Field(..., description="Unique database identifier for the operator")
    distance_km: float = Field(..., gt=0, description="Total trip distance must be greater than zero")
    traffic_density: float = Field(..., ge=0, le=1, description="Traffic density coefficient bounded between 0 and 1")

@app.get("/api/v1/health")
def check_health():
    return {"status": "healthy", "milestone": "Day 10 Core Parameter Security Standard Reached"}

@app.post("/api/v1/trips/verify")
def verify_and_log_trip(payload: TripPayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Security Upgrade: Using parameterized execution placeholders (%s) to sanitize raw network arguments
        driver_query = "SELECT * FROM drivers WHERE driver_id = %s"
        cursor.execute(driver_query, (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            raise HTTPException(status_code=404, detail="Driver validation failed. Secure ID verification rejected.")
        
        return {
            "status": "synchronized",
            "message": "Telemetry securely matched against active driver profiles.",
            "data": {
                "driver_name": driver_record.get("name", "Active Operator"),
                "assigned_distance": payload.distance_km,
                "traffic_coefficient": payload.traffic_density
            }
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Secure database channel connection error: {str(err)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/v1/trips")
def fetch_historical_trips(limit: int = 10):
    try:
        # Prevent boundary breaks by enforcing pagination limits
        if limit > 100:
            limit = 100
            
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Security Upgrade: Parameterizing the limit operator to block execution manipulation
        query = """
            SELECT t.trip_id, t.distance_km, t.traffic_density, d.name AS driver_name 
            FROM trips t
            LEFT JOIN drivers d ON t.driver_id = d.driver_id
            ORDER BY t.trip_id DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        records = cursor.fetchall()
        
        return {
            "status": "success",
            "count": len(records),
            "data": records
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database operational read exception: {str(err)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()