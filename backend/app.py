from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
import pandas as pd
import joblib         # Uncomment when model file is ready
import numpy as np    # Uncomment when model file is ready

import sys
from pathlib import Path
model_dir = Path(__file__).parent / "model"
if str(model_dir) not in sys.path:
    sys.path.append(str(model_dir))
import custom_transformers

app = FastAPI()

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("Validation Error Details:", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

origins = [
    "http://localhost:5500",                  # VS Code Live Server (Frontend)
    "http://127.0.0.1:5500",                  # VS Code Five Server
    "http://localhost:5173",                  # Vite / React default (if you use it)
    "https://autoval-threebytes.vercel.app",  # Exact Vercel deployment URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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
    print("ML Engine successfully initialized and online.")
except Exception as e:
    print(f"ML Engine offline: {e}")
    model = None

@app.get("/")
def check_status():
    return {
        "status": "success", 
        "message": "FastAPI engine matches server routing configuration."
    }

@app.post("/predict")
def predict_car_value(car: CarInput):
    current_year = 2026
    car_year = int(car.year)
    car_mileage = int(car.odometer)
    car_brand = car.manufacturer
    age = max(0, current_year - car_year)

    # Uncomment when model file is ready
    if model is not None:
        input_data = pd.DataFrame([{
            "manufacturer": car.manufacturer,
            "model": car.model,
            "year": car_year,
            "odometer": car_mileage,
            "condition": car.condition,
            "cylinders": car.cylinders,
            "fuel": car.fuel,
            "title_status": car.title_status,
            "transmission": car.transmission,
            "drive": car.drive,
            "size": car.size,
            "type": car.type
        }])
        final_estimate = round(float(model.predict(input_data)[0]))

        return {
            "success": True,
            "brand": f"{car.manufacturer.capitalize()} {car.model.capitalize()}",
            "year": car_year,
            "estimatedValue": f"${final_estimate:,}",
            # Temporary/fake values
            "dealMetrics": {"status": "fair_price", "label": "ML Predicted Market Price"},
            "marketInsights": {
                "averagePriceForYear": "Calculated by ML",
                "depreciationRate": "Determined by ML data drift",
                "mileageImpact": " factored into ML weights"
            }
        }

    return {
        "success": True,
        "brand": f"{car_brand.capitalize()} Vehicle",
        "year": car_year,
        "estimatedValue": f"${final_estimate:,}",
        "dealMetrics": {
            "status": deal_rating,
            "label": deal_label
        },
        "marketInsights": {
            "averagePriceForYear": f"${baseline_price_for_year:,}",
            "depreciationRate": f"{round(annual_depreciation_rate * 100)}% annually",
            "mileageImpact": f"-${round(mileage_penalty):,}"
        }
    }

@app.post("/market-trends")
def calculate_trends(car: CarInput):
    # Temporary formulas start (Delete when model file is ready) ===================================================================
    # current_year = 2026
    # car_year = int(car.year) if car.year else 2026
    # age = max(0, current_year - car_year)
    
    car_brand = car.manufacturer
    
    starting_price = 65000 if car_brand == 'luxury' else 26000
    if car.condition == 'excellent': starting_price *= 1.12
    elif car.condition == 'poor': starting_price *= 0.65
    
    if car.transmission == 'manual':
        starting_price = starting_price * 1.05 if car_brand == 'luxury' else starting_price * 0.93

    decay_factor = 0.82 if car_brand == 'luxury' else 0.90 
    mileage_labels = ["10k mi", "30k mi", "50k mi", "70k mi", "90k mi", "110k mi+"]
    
    depreciation_prices = []
    for index, _ in enumerate(mileage_labels):
        step_penalty = math.pow(decay_factor, index)
        baseline_floor = 4000 if car_brand == 'luxury' else 2000
        calculated_step = round(max(baseline_floor, starting_price * step_penalty))
        depreciation_prices.append(calculated_step)
    # Temporary formulas end (Delete when model file is ready) ===================================================================

    return {
        "success": True,
        "mileageLabels": mileage_labels,
        "depreciationPrices": depreciation_prices
    }