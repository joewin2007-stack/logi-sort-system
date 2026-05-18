# 🚛 Logi-Sort System

The Logi-Sort System is a scalable logistics optimization and machine learning prediction platform built over an engineering sprint. The core architecture integrates an automated pipeline handling everything from workspace initialization and mock data generation to data profiling, feature engineering, and robust model validation.

The backend infrastructure leverages a high-performance REST API gateway built with FastAPI to manage real-time logistical telemetry validations against a local MySQL relational database layer. Incoming network payloads containing driver assignments and trip telemetry are securely processed, validated, and evaluated against relational schemas to ensure strict data integrity.

## 🛠️ Execution & Deployment

### System Dependencies
Ensure your python virtual environment is activated, then install the core stack requirements:
```bash
pip install fastapi uvicorn mysql-connector-python pydantic