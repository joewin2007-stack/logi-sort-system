import sys
import pandas as pd
import joblib

def main():
    print("🔮 Logi-Sort Production Inference Engine")
    print("-----------------------------------------")

    # 1. Check if the user provided the exact inputs needed
    # sys.argv contains the list of arguments passed in the terminal.
    # sys.argv[0] is always the script name itself, so we expect 4 items total.
    if len(sys.argv) != 4:
        print("❌ Error: Missing arguments!")
        print("💡 Usage: python scripts/predict_delivery.py <distance_km> <traffic_density> <weather_impact>")
        print("📋 Example: python scripts/predict_delivery.py 120.5 8 1.5")
        sys.exit(1)

    # 2. Parse inputs from the command line strings into decimal numbers
    try:
        distance = float(sys.argv[1])
        traffic = float(sys.argv[2])
        weather = float(sys.argv[3])
    except ValueError:
        print("❌ Error: All arguments must be numeric values (integers or decimals).")
        sys.exit(1)

    # 3. Load the pre-trained ML Model
    try:
        model = joblib.load('ml_model/logistics_model.pkl')
    except FileNotFoundError:
        print("❌ Error: Trained model 'logistics_model.pkl' not found.")
        sys.exit(1)

    print(f"📦 Live Inputs Parsed Successfully:")
    print(f"   - Distance: {distance} km")
    print(f"   - Traffic Density: {traffic}/10")
    print(f"   - Weather Multiplier: {weather}\n")

    # 4. Format data structure matching model's training expectations
    feature_names = ['distance_km', 'traffic_density', 'weather_impact']
    input_data = pd.DataFrame([[distance, traffic, weather]], columns=feature_names)

    # 5. Execute Instant O(1) Prediction
    predicted_time = model.predict(input_data)

    print("=========================================")
    print(f"🚀 Live AI ETA Prediction: {round(predicted_time[0], 2)} minutes")
    print("=========================================")

if __name__ == "__main__":
    main()