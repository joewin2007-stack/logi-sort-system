import mysql.connector
from fastapi import HTTPException, status
from scripts.config import DB_CONFIG
import os  # <-- Add this import at the top if it isn't there
from dotenv import load_dotenv  # <-- Add this import at the top

load_dotenv()  # <-- Load environment variables from .env file

def get_db_connection():
    """Generates a dynamic database connection pulling parameters directly from environment variable pools."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "logi_sort"),
        port=int(os.getenv("DB_PORT", 3306))
    )

def initialize_database_schemas():
    """Self-healing setup routine to safely prepare missing database tables on startup."""
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
        print("🗄️ Database modules checked and safely initialized.")
    except mysql.connector.Error as db_err:
        print(f"⚠️ Safe Database Startup Notice: Seeding bypassed. Engine running. Log: {str(db_err)}")