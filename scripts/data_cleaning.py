import pandas as pd
import mysql.connector
import os

def clean_logistics_data():
    # 1. Database Connection
    config = {
        'user': 'root',
        'password': '', # Ensure this matches your generator
        'host': '127.0.0.1',
        'database': 'logi_sort'
    }

    try:
        print("📥 Connecting to MySQL and fetching data...")
        conn = mysql.connector.connect(**config)
        query = "SELECT * FROM trip_logs"
        
        # Load into Pandas
        df = pd.read_sql(query, conn)
        conn.close()

        print(f"✅ Data fetched: {len(df)} rows found.")

        # 2. Fix Data Types (Crucial step!)
        # Converting from objects/strings to floats/integers for math
        numeric_cols = ['distance_km', 'traffic_density', 'weather_impact', 'actual_time_mins', 'day_of_week', 'hour_of_day']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. Data Cleaning & Feature Engineering
        # Remove any rows that failed conversion (NaNs)
        df = df.dropna()

        # Calculate Speed (Feature Engineering)
        # speed = distance / (time in hours)
        df['avg_speed_kmh'] = df['distance_km'] / (df['actual_time_mins'] / 60)

        # 4. Outlier Detection (Andrew Ng concept)
        # Remove unrealistic speeds (e.g., > 150km/h or < 5km/h)
        initial_count = len(df)
        df = df[(df['avg_speed_kmh'] <= 150) & (df['avg_speed_kmh'] >= 5)]
        print(f"🧹 Removed {initial_count - len(df)} outliers based on speed.")

        # 5. Dataset Overview
        print("\n--- CLEANED DATASET OVERVIEW ---")
        print(df.info())
        print("\n--- SAMPLE DATA ---")
        print(df.head())

        # 6. Export to CSV for ML Training
        if not os.path.exists('data'):
            os.makedirs('data')
        
        output_path = 'data/cleaned_trips.csv'
        df.to_csv(output_path, index=False)
        print(f"\n🚀 Success! Cleaned data saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error during cleaning: {e}")

if __name__ == "__main__":
    clean_logistics_data()