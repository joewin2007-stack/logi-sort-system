from fastapi import FastAPI, HTTPException, status
import mysql.connector
from pydantic import BaseModel, Field
import joblib
import os

app = FastAPI(title="Logi-Sort Resilient API Gateway - Day 13")

# Centralized database configuration management
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": '',  # Put your real local MySQL password here
    "database": "logi_sort"
}

MODEL_PATH = os.path.join("ml_model", "delivery_model.pkl")
model = None

def get_db_connection():
    """Attempts to establish a database channel; throws a clean operational error if MySQL is down."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        # If MySQL is stopped or the password fails, raise a clean HTTP 503 Service Unavailable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database warehouse is completely offline or unreachable: {str(err)}"
        )

@app.on_event("startup")
def startup_pipeline():
    """Self-healing setup: Prepares the ML brain and attempts to initialize database layers."""
    global model
    
    # 1. Load the Machine Learning model if available
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("🧠 Success: Machine Learning prediction engine loaded into memory.")
        else:
            print("⚠️ Warning: ml_model/delivery_model.pkl not found. Running with mock estimation fallback.")
    except Exception as e:
        print(f"❌ Failed to load ML model: {str(e)}")

    # 2. Resilient Database Initialization
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                driver_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                vehicle_type VARCHAR(50) NOT NULL
            );
        """)
        
        cursor.execute("""
            INSERT INTO drivers (driver_id, name, vehicle_type) VALUES
            (1, 'Alex Johnson', 'Semi-Truck'),
            (2, 'Sarah Connor', 'Delivery Van'),
            (3, 'Michael Scott', 'Box Truck')
            ON DUPLICATE KEY UPDATE name=name;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id INT AUTO_INCREMENT PRIMARY KEY,
                driver_id INT,
                distance_km FLOAT NOT NULL,
                traffic_density FLOAT NOT NULL,
                predicted_duration_minutes FLOAT NOT NULL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
            );
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("🗄️ Success: Database tables initialized and verified.")
    except mysql.connector.Error as db_err:
        print(f"⚠️ Resilient Startup Notice: Database couldn't auto-initialize. API will run, but database routes will report offline status. Error: {str(db_err)}")


class TripPayload(BaseModel):
    driver_id: int = Field(..., description="Unique database identifier for the operator")
    distance_km: float = Field(..., gt=0, description="Total trip distance must be greater than zero")
    traffic_density: float = Field(..., ge=0, le=1, description="Traffic density coefficient bounded between 0 and 1")


@app.get("/api/v1/health")
def check_health():
    """Comprehensive health check checking both server runtime status and live database availability."""
    db_alive = False
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            db_alive = True
            conn.close()
    except:
        db_alive = False

    return {
        "status": "healthy", 
        "database_connected": db_alive,
        "model_loaded": model is not None,
        "milestone": "Day 13 Production Resilience Standards Enforced"
    }


@app.post("/api/v1/trips/verify")
def verify_predict_and_log_trip(payload: TripPayload):
    # This call safely checks if database is reachable before executing any logic
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Driver verification check
        driver_query = "SELECT * FROM drivers WHERE driver_id = %s"
        cursor.execute(driver_query, (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            raise HTTPException(status_code=404, detail=f"Driver ID {payload.driver_id} not found.")
        
        # 2. Process ML prediction inference
        if model is not None:
            input_features = [[payload.distance_km, payload.traffic_density]]
            predicted_duration_mins = float(model.predict(input_features)[0])
            prediction_source = "Production ML Inference Engine"
        else:
            predicted_duration_mins = (payload.distance_km * 1.5) + (payload.traffic_density * 30.0)
            prediction_source = "Fallback Heuristic Baseline"

        # 3. Safe transaction write-back
        insert_query = """
            INSERT INTO trips (driver_id, distance_km, traffic_density, predicted_duration_minutes)
            VALUES (%s, %s, %s, %s)
        """
        insert_values = (payload.driver_id, payload.distance_km, payload.traffic_density, round(predicted_duration_mins, 2))
        cursor.execute(insert_query, insert_values)
        
        # Save to disk
        connection.commit()
        new_trip_id = cursor.lastrowid

        return {
            "status": "synchronized",
            "message": "Telemetry verified, predicted, and logged permanently to database.",
            "logged_trip_id": new_trip_id,
            "routing_metadata": {
                "driver_name": driver_record.get("name"),
                "assigned_distance_km": payload.distance_km,
                "traffic_density_coefficient": payload.traffic_density
            },
            "predictive_analytics": {
                "estimated_duration_minutes": round(predicted_duration_mins, 2),
                "engine_source": prediction_source
            }
        }
        
    except mysql.connector.Error as err:
        # CRITICAL RESILIENCE RULE: If the write fails halfway through, roll back changes to avoid broken records
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database mid-transaction operational crash. Safe rollback triggered: {str(err)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.get("/api/v1/trips")
def fetch_historical_trips(limit: int = 10):
    if limit > 100:
        limit = 100
        
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT t.trip_id, t.distance_km, t.traffic_density, t.predicted_duration_minutes, d.name AS driver_name 
            FROM trips t
            LEFT JOIN drivers d ON t.driver_id = d.driver_id
            ORDER BY t.trip_id DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        records = cursor.fetchall()
        return {"status": "success", "count": len(records), "data": records}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database persistent read exception: {str(err)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()