from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
import sys
import joblib
import pandas as pd

sys.path.append('model')
from custom_transformer import RareManufacturerGrouper, ModelTargetEncoder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarInput(BaseModel):
    manufacturer: str
    model: str
    year: int
    odometer: int
    condition: str | None = None
    cylinders: str | None = None
    fuel: str | None = None
    title_status: str | None = None
    transmission: str | None = None
    drive: str | None = None
    size: str | None = None
    type: str | None = None

try:
    model = joblib.load("model/car_price_pipeline.joblib")
except Exception as e:
    print(f"ML Engine offline: {e}")
    model = None

@app.get("/")
def check_status():
    return {"status": "success", "message": "FastAPI engine matches server routing configuration."}

@app.post("/predict")
def predict_car_value(car: CarInput):
    if model is None:
        return {"success": False, "message": "ML Engine offline."}

    input_df = pd.DataFrame([{
        "manufacturer": car.manufacturer,
        "model": car.model,
        "year": car.year,
        "odometer": car.odometer,
        "condition": car.condition or "Unknown",
        "cylinders": car.cylinders or "Unknown",
        "fuel": car.fuel or "Unknown",
        "title_status": car.title_status or "Unknown",
        "transmission": car.transmission or "Unknown",
        "drive": car.drive or "Unknown",
        "size": car.size or "Unknown",
        "type": car.type or "Unknown",
    }])

    final_estimate = round(float(model.predict(input_df)[0]))

    return {
        "success": True,
        "brand": f"{car.manufacturer.capitalize()} {car.model.capitalize()}",
        "year": car.year,
        "estimatedValue": f"${final_estimate:,}",
        "dealMetrics": {
            "status": "fair_price",
            "label": "ML Predicted Market Price"
        },
        "marketInsights": {
            "averagePriceForYear": "Calculated by ML",
            "depreciationRate": "Determined by ML data drift",
            "mileageImpact": "Factored into ML weights"
        }
    }

@app.post("/market-trends")
def calculate_trends(car: CarInput):
    # TODO: replace with real model, needs multiple predict() calls at simulated mileage steps
    starting_price = 65000 if car.manufacturer == 'luxury' else 26000
    if car.condition == 'excellent': starting_price *= 1.12
    elif car.condition == 'poor': starting_price *= 0.65

    if car.transmission == 'manual':
        starting_price = starting_price * 1.05 if car.manufacturer == 'luxury' else starting_price * 0.93

    decay_factor = 0.82 if car.manufacturer == 'luxury' else 0.90
    mileage_labels = ["10k mi", "30k mi", "50k mi", "70k mi", "90k mi", "110k mi+"]

    depreciation_prices = []
    for index, _ in enumerate(mileage_labels):
        step_penalty = math.pow(decay_factor, index)
        baseline_floor = 4000 if car.manufacturer == 'luxury' else 2000
        calculated_step = round(max(baseline_floor, starting_price * step_penalty))
        depreciation_prices.append(calculated_step)

    return {
        "success": True,
        "mileageLabels": mileage_labels,
        "depreciationPrices": depreciation_prices
    }