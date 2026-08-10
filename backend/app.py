import os
import sys
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

# 1. System Paths & Environment Setup ===================================================================================================
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# Ensure local modules (model transformers and database adapters) are on sys.path
for path in [BASE_DIR / "model", BASE_DIR / "database"]:
    if str(path) not in sys.path:
        sys.path.append(str(path))

import chart_mapper
import custom_transformers  # Required for joblib model unpickling

# 2. FastAPI Setup ======================================================================================================================
app = FastAPI(title="AutoVal ML API")

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "https://autoval-threebytes.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

USD_TO_PHP = 58.5

# 3. Schemas & ML Model Loading =========================================================================================================
class CarInput(BaseModel):
    manufacturer: str
    model: str
    year: int
    odometer: int
    condition: str | None = "Unknown"
    cylinders: str | None = "Unknown"
    fuel: str | None = "Unknown"
    title_status: str | None = "Unknown"
    transmission: str | None = "automatic"
    drive: str | None = "Unknown"
    size: str | None = "Unknown"
    type: str | None = "Unknown"


try:
    model = joblib.load(BASE_DIR / "model" / "car_price_pipeline.joblib")
    print("ML Engine successfully initialized and online.")
except Exception as e:
    print(f"ML Engine offline: {e}")
    model = None


# 4. Helper Functions ===================================================================================================================
def build_feature_dict(car: CarInput, odometer_override: int | None = None) -> dict:
    """Helper to standardize Pandas DataFrame input format across endpoints."""
    return {
        "manufacturer": car.manufacturer,
        "model": car.model,
        "year": int(car.year),
        "odometer": odometer_override if odometer_override is not None else int(car.odometer),
        "condition": car.condition or "Unknown",
        "cylinders": car.cylinders or "Unknown",
        "fuel": car.fuel or "Unknown",
        "title_status": car.title_status or "Unknown",
        "transmission": car.transmission or "automatic",
        "drive": car.drive or "Unknown",
        "size": car.size or "Unknown",
        "type": car.type or "Unknown",
    }

def log_prediction_to_db(car: CarInput, php_price: float):
    """Inserts user input specs and estimated price into Neon DB matching the updated schema."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set. Skipping log.")
        return

    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO prediction_logs 
                    (year, manufacturer, model, condition, cylinders, fuel, odometer, title_status, transmission, drive, size, type, estimated_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (
                    int(car.year),
                    car.manufacturer.lower(),
                    car.model.lower(),
                    car.condition,
                    car.cylinders,
                    car.fuel,
                    int(car.odometer),
                    car.title_status,
                    car.transmission,
                    car.drive,
                    car.size,
                    car.type,
                    php_price
                ))
                conn.commit()
                print("Prediction successfully logged to Neon DB.")
    except Exception as e:
        print(f"Failed to log prediction to DB: {e}")

# 5. Routes =============================================================================================================================
@app.get("/")
def check_status():
    return {"status": "success", "message": "FastAPI engine online."}


@app.get("/chart-data")
def fetch_chart_data():
    try:
        data = chart_mapper.fetch_all_data()
        return {"success": True, "data": data}
    except Exception as e:
        print(f"Neon DB Error: {e}")
        return {"success": False, "error": str(e), "data": []}


@app.post("/predict")
def predict_car_value(car: CarInput):
    if model is None:
        return {"success": False, "message": "ML Model unavailable"}

    input_df = pd.DataFrame([build_feature_dict(car)])
    
    # Run single prediction inference
    raw_usd_prediction = float(model.predict(input_df)[0])
    php_estimate = round(raw_usd_prediction * USD_TO_PHP)

    # log car specs and price estimate to db
    log_prediction_to_db(car, php_estimate)

    # 10% tolerance boundary calculation
    min_value = round(php_estimate * 0.90)
    max_value = round(php_estimate * 1.10)

    return {
        "success": True,
        "brand": f"{car.manufacturer.title()} {car.model.title()}",
        "year": int(car.year),
        "estimatedValue": f"₱{php_estimate:,}",
        "range": {
            "min": f"₱{min_value:,}",
            "max": f"₱{max_value:,}",
        },
        "rawEstimates": {
            "min": min_value,
            "target": php_estimate,
            "max": max_value,
        },
        "dealMetrics": {"status": "fair_price", "label": "ML Predicted Market Price"},
    }


@app.post("/market-trends")
def calculate_trends(car: CarInput):
    mileage_steps = [10000, 30000, 50000, 70000, 90000, 110000]
    mileage_labels = ["10k mi", "30k mi", "50k mi", "70k mi", "90k mi", "110k mi+"]

    if model is None:
        return {
            "success": False,
            "message": "ML Model unavailable",
            "mileageLabels": mileage_labels,
            "depreciationPrices": [],
        }

    try:
        # Build batch inference dataframe with varying odometer values
        batch_rows = [build_feature_dict(car, odo) for odo in mileage_steps]
        input_df = pd.DataFrame(batch_rows)

        raw_predictions = model.predict(input_df)
        depreciation_prices = [
            max(0, round(float(price) * USD_TO_PHP)) for price in raw_predictions
        ]

        return {
            "success": True,
            "mileageLabels": mileage_labels,
            "depreciationPrices": depreciation_prices,
        }

    except Exception as e:
        print(f"ML Trend Calculation Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "mileageLabels": mileage_labels,
            "depreciationPrices": [],
        }