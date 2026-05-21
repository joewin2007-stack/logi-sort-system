from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel, Field
import joblib
import os

app = FastAPI(title="Logi-Sort Production API Gateway - Day 11")

# Centralized configuration management
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": '',  # Replace with your actual database password
    "database": "logi_sort"
}

# Define paths to retrieve your Day 5 machine learning brain artifacts
MODEL_PATH = os.path.join("ml_model", "delivery_model.pkl")

# Initialize global placeholder variables for our model components
model = None

@app.on_event("startup")
def load_ml_artifacts():
    """Load the machine learning brain files into system memory on boot."""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("🧠 Success: Machine Learning prediction engine loaded into memory.")
        else:
            print("⚠️ Warning: ml_model/delivery_model.pkl not found. Running with mock estimation fallback.")
    except Exception as e:
        print(f"❌ Failed to load ML model files: {str(e)}")

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class TripPayload(BaseModel):
    driver_id: int = Field(..., description="Unique database identifier for the operator")
    distance_km: float = Field(..., gt=0, description="Total trip distance must be greater than zero")
    traffic_density: float = Field(..., ge=0, le=1, description="Traffic density coefficient bounded between 0 and 1")

@app.get("/api/v1/health")
def check_health():
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "milestone": "Day 11 Dynamic Intelligence Gateway Active"
    }

@app.post("/api/v1/trips/verify")
def verify_and_predict_trip(payload: TripPayload):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify driver existence to preserve system relational integrity
        driver_query = "SELECT * FROM drivers WHERE driver_id = %s"
        cursor.execute(driver_query, (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            raise HTTPException(status_code=404, detail="Driver validation failed. Unknown identity parameter.")
        
        # --- THE DAY 11 BRAIN CONNECTION ---
        # If your trained model file is loaded, calculate the real mathematical prediction.
        # Otherwise, fall back to a safe programmatic placeholder formula.
        if model is not None:
            # Structuring our inputs matching exactly how your Day 5 engine expects them: [[distance, traffic]]
            input_features = [[payload.distance_km, payload.traffic_density]]
            predicted_array = model.predict(input_features)
            predicted_duration_mins = float(predicted_array[0])
            prediction_source = "Production ML Inference Engine"
        else:
            # Fallback estimation logic if your pkl file hasn't been moved into the directory yet
            predicted_duration_mins = (payload.distance_km * 1.5) + (payload.traffic_density * 30.0)
            prediction_source = "Fallback Heuristic Baseline"

        return {
            "status": "synchronized",
            "message": "Telemetry matched and analyzed successfully.",
            "routing_metadata": {
                "driver_name": driver_record.get("name", "Active Operator"),
                "assigned_distance_km": payload.distance_km,
                "traffic_density_coefficient": payload.traffic_density
            },
            "predictive_analytics": {
                "estimated_duration_minutes": round(predicted_duration_mins, 2),
                "engine_source": prediction_source
            }
        }
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database communication failure: {str(err)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/v1/trips")
def fetch_historical_trips(limit: int = 10):
    try:
        if limit > 100:
            limit = 100
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT t.trip_id, t.distance_km, t.traffic_density, d.name AS driver_name 
            FROM trips t
            LEFT JOIN drivers d ON t.driver_id = d.driver_id
            ORDER BY t.trip_id DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        records = cursor.fetchall()
        
        return {"status": "success", "count": len(records), "data": records}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database read failure: {str(err)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()