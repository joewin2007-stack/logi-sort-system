import pandas as pd
import joblib

def predict_new_trip():
    print("🔮 Logi-Sort Production Inference Engine")
    print("-----------------------------------------")

    # 1. Load the saved brain (O(1) complexity)
    try:
        model = joblib.load('ml_model/logistics_model.pkl')
    except FileNotFoundError:
        print("❌ Error: Saved model not found! Run train_model.py first.")
        return

    # 2. Accept New Real-Time Inputs
    # Let's simulate an urgent upcoming delivery request
    distance = 85.5        # Distance in kilometers
    traffic = 7            # Traffic density scale (1 to 10)
    weather = 1.8          # Weather impact score (1.0 = clear, 2.0 = severe storm)

    print(f"📦 Incoming Route details:")
    print(f"   - Distance: {distance} km")
    print(f"   - Traffic Density: {traffic}/10")
    print(f"   - Weather Multiplier: {weather}\n")

    # 3. Format inputs exactly how the model expects them
    # Remember the warning from yesterday? We use DataFrame to give it explicit feature names.
    feature_names = ['distance_km', 'traffic_density', 'weather_impact']
    new_data = pd.DataFrame([[distance, traffic, weather]], columns=feature_names)

    # 4. Predict!
    predicted_time = model.predict(new_data)

    print("=========================================")
    print(f"🚀 AI ETA Prediction: {round(predicted_time[0], 2)} minutes")
    print("=========================================")

if __name__ == "__main__":
    predict_new_trip()