# 🚚 Logi-Sort: Smart Logistics Predictive API

Logi-Sort is a production-ready backend system designed for logistics and delivery companies. The application validates live trip data, checks driver records against a relational database, and uses a machine learning model to calculate real-time travel duration (ETA) predictions.

## 🏗️ Architecture Overview

The project is built using an enterprise modular layout:
* **The Warehouse (Database):** A MySQL layer tracking active `drivers` and permanent historical `trips`.
* **The Brain (AI Engine):** A Scikit-Learn Linear Regression model trained to predict travel duration based on trip distance and traffic density.
* **The Front Desk (API Gateway):** A modular FastAPI architecture that securely handles incoming telemetry requests, enforces strict data boundaries, and writes transaction logs back to disk.

## 📂 Modular Structure

```text
scripts/
├── config.py            # Centralized database credentials and file paths
├── database.py          # MySQL connections and self-healing table setup
├── schemas.py           # Data validation rules (Pydantic models)
└── app.py               # Main API routing and ML initialization engine