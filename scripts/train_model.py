import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib # To save the model

# 1. Load the clean data
df = pd.read_csv('data/cleaned_trips.csv')

# 2. Select Features (X) and Target (y)
X = df[['distance_km', 'traffic_density', 'weather_impact']]
y = df['actual_time_mins']

# 3. Split data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and Train the Model
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Check Accuracy
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

print(f"✅ Model Trained!")
print(f"📊 Average Prediction Error: {round(error, 2)} minutes")

# 6. Test a "Real" Scenario
# Predict time for: 50km, Traffic level 8, Stormy weather (1.9)
test_trip = [[50, 8, 1.9]]
predicted_time = model.predict(test_trip)
print(f"🔮 Predicted time for test trip: {round(predicted_time[0], 2)} mins")

joblib.dump(model, 'ml_model/logistics_model.pkl')
print("💾 Model saved to ml_model/logistics_model.pkl")