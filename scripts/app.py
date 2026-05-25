from fastapi import FastAPI, HTTPException
import mysql.connector
import joblib
import os

# Clean, explicit relative imports from our new module design
from scripts.config import MODEL_PATH
from scripts.schemas import TripPayload
from scripts.database import get_db_connection, initialize_database_schemas

app = FastAPI(title="Logi-Sort Enterprise Modular API Gateway - Day 14")

model = None

@app.on_event("startup")
def startup_pipeline():
    """Prepares system sub-modules cleanly on boot."""
    global model
    
    # 1. Initialize self-healing database schemas
    initialize_database_schemas()
    
    # 2. Load the Machine Learning engine
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("🧠 Success: Machine Learning prediction engine loaded into memory.")
        else:
            print("⚠️ Warning: ml_model file not found. Running with mock estimation fallback.")
    except Exception as e:
        print(f"❌ Failed to load ML model: {str(e)}")


@app.get("/api/v1/health")
def check_health():
    return {
        "status": "healthy",
        "modular_architecture": True,
        "milestone": "Day 14 Modular Clean Code Standards Achieved"
    }


@app.post("/api/v1/trips/verify")
def verify_predict_and_log_trip(payload: TripPayload):
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Validate driver profiles
        cursor.execute("SELECT * FROM drivers WHERE driver_id = %s", (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            raise HTTPException(status_code=404, detail=f"Driver ID {payload.driver_id} not found.")
        
        # Dynamic AI routing prediction
        if model is not None:
            input_features = [[payload.distance_km, payload.traffic_density]]
            predicted_duration_mins = float(model.predict(input_features)[0])
            prediction_source = "Production ML Inference Engine"
        else:
            predicted_duration_mins = (payload.distance_km * 1.5) + (payload.traffic_density * 30.0)
            prediction_source = "Fallback Heuristic Baseline"

        # Safe relational write-back execution
        insert_query = """
            INSERT INTO trips (driver_id, distance_km, traffic_density, predicted_duration_minutes)
            VALUES (%s, %s, %s, %s)
        """
        insert_values = (payload.driver_id, payload.distance_km, payload.traffic_density, round(predicted_duration_mins, 2))
        cursor.execute(insert_query, insert_values)
        
        connection.commit()
        new_trip_id = cursor.lastrowid

        return {
            "status": "synchronized",
            "message": "Telemetry processed and logged via modular service pipeline.",
            "logged_trip_id": new_trip_id,
            "routing_metadata": {
                "driver_name": driver_record.get("name"),
                "assigned_distance_km": payload.distance_km
            },
            "predictive_analytics": {
                "estimated_duration_minutes": round(predicted_duration_mins, 2),
                "engine_source": prediction_source
            }
        }
        
    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database operational write crash: {str(err)}")
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
        raise HTTPException(status_code=500, detail=f"Database read crash: {str(err)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()