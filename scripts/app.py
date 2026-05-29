from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import joblib
import os
import time
import logging

# Clean relative imports from our module design
from scripts.config import MODEL_PATH
from scripts.schemas import TripPayload
from scripts.database import get_db_connection, initialize_database_schemas

# Configure production file logger alongside terminal stream outputs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("logi_sort_metrics")

app = FastAPI(title="Logi-Sort Enterprise Monitored API Gateway - Day 18")

# 1. --- THE DAY 18 CORS SECURITY MATRIX ---
# Define which origins/web addresses are allowed to call our logistics API
ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Common React local development port
    "http://localhost:5173",      # Common Vite/Vue local development port
    "http://127.0.0.1:5500",      # VS Code Live Server extension port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,      # Permits specific frontend domains
    allow_credentials=True,             # Allows cookies and authentication tokens across origins
    allow_methods=["GET", "POST"],      # Binds network actions to strictly required methods
    allow_headers=["*"],                # Permits all standard client request headers
    expose_headers=["X-Process-Latency-MS"] # Explicitly lets browsers read our Day 17 performance timer
)

model = None

@app.on_event("startup")
def startup_pipeline():
    """Prepares system sub-modules cleanly on boot."""
    global model
    initialize_database_schemas()
    
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info("🧠 Success: Machine Learning prediction engine loaded into memory.")
        else:
            logger.warning("⚠️ Warning: ml_model file not found. Running with mock estimation fallback.")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {str(e)}")


@app.middleware("http")
async def log_performance_telemetry(request: Request, call_next):
    """Interceptors that measure the exact performance time of incoming API requests."""
    start_time = time.time()
    response = await call_next(request)
    process_duration_ms = (time.time() - start_time) * 1000
    
    logger.info(
        f"Route: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Latency: {process_duration_ms:.2f}ms"
    )
    
    response.headers["X-Process-Latency-MS"] = f"{process_duration_ms:.2f}"
    return response


@app.get("/api/v1/health")
def check_health():
    return {
        "status": "healthy",
        "cors_policy": "enforced",
        "milestone": "Day 18 Cross-Origin Resource Management Operational"
    }


@app.post("/api/v1/trips/verify")
def verify_predict_and_log_trip(payload: TripPayload):
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM drivers WHERE driver_id = %s", (payload.driver_id,))
        driver_record = cursor.fetchone()
        
        if not driver_record:
            raise HTTPException(status_code=404, detail=f"Driver ID {payload.driver_id} not found.")
        
        if model is not None:
            input_features = [[payload.distance_km, payload.traffic_density]]
            predicted_duration_mins = float(model.predict(input_features)[0])
            prediction_source = "Production ML Inference Engine"
        else:
            predicted_duration_mins = (payload.distance_km * 1.5) + (payload.traffic_density * 30.0)
            prediction_source = "Fallback Heuristic Baseline"

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
            "message": "Telemetry processed and logged via monitored service pipeline.",
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