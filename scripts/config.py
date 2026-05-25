import os

# Centralized environment configurations
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": '',  # Put your real local MySQL password here
    "database": "logi_sort"
}

MODEL_PATH = os.path.join("ml_model", "delivery_model.pkl")