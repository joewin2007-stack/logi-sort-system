# 🚛 Logi-Sort System
A 30-day engineering challenge to build a logistics optimization and ML prediction system.

## 📊 Current Project Status: **Day 5 Complete**

### 🏗️ Day 1-2: Data Infrastructure
- **Git & MySQL:** Established repository structure and relational schema.
- **Data Generation:** Built `data_generator.py` to simulate 5,000 trips with synthetic noise.

### 🧹 Day 3-4: Data Engineering & Cleaning
- **Pipeline:** Developed `data_cleaning.py` to bridge MySQL and Python/Pandas.
- **Preprocessing:** Performed type conversion, outlier removal (speed filtering), and feature engineering (`avg_speed_kmh`).
- **Persistence:** Generated `cleaned_trips.csv` for model training.

### 🧠 Day 5: Machine Learning Implementation
- **Model:** Built a **Linear Regression** model using Scikit-Learn.
- **Performance:** Achieved a **Mean Absolute Error (MAE) of 4.94 minutes**.
- **Features:** Trained on Distance, Traffic Density, and Weather Impact.
- **Artifacts:** Exported trained model to `ml_model/logistics_model.pkl` for future inference.

### 🔮 Day 6: Production Inference Engine
- **Pipeline:** Built `predict_delivery.py` to leverage the saved model artifacts.
- **Optimization:** Shifted from training-time complexity to production-ready $O(1)$ inference.
- **Validation:** Resolved Pandas feature-name warnings by formalizing data layout inputs.

## 🛠️ How to Run
1. Generate: `python scripts/data_generator.py`
2. Clean: `python scripts/data_cleaning.py`
3. Train: `python scripts/train_model.py`