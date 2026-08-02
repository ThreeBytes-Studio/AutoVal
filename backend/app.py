from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
# import joblib         # Uncomment when model file is ready
# import numpy as np    # Uncomment when model file is ready

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarInput(BaseModel):
    brand: str
    year: str or int or None = None
    mileage: str or int or None = None
    transmission: str or None = None
    condition: str or None = None

# Uncomment when model file is ready
# try:
#     model = joblib.load("car_model.joblib")
# except Exception as e:
#     print(f"ML Engine offline: {e}")
#     model = None

@app.get("/")
def check_status():
    return {"status": "success", "message": "FastAPI engine matches server routing configuration."}

@app.post("/predict")
def predict_car_value(car: CarInput):
    current_year = 2026
    car_year = int(car.year)
    car_mileage = int(car.mileage)
    age = max(0, current_year - car_year)

    # Uncomment when model file is ready
    # if model is not None:
    #     features = np.array([[car.brand, car_year, car_mileage, car.transmission, car.condition]])
    #     final_estimate = round(float(model.predict(features)[0]))
    #     
    #     return {
    #         "success": True,
    #         "brand": f"{car.brand.capitalize()} Vehicle",
    #         "year": car_year,
    #         "estimatedValue": f"${final_estimate:,}",
    #         "dealMetrics": {"status": "fair_price", "label": "ML Predicted Market Price"},
    #         "marketInsights": {
    #             "averagePriceForYear": "Calculated by ML",
    #             "depreciationRate": "Determined by ML data drift",
    #             "mileageImpact": " factored into ML weights"
    #         }
    #     }

    # Temporary formulas start (Delete when model file is ready) ===================================================================
    floor_price = 4000 if car.brand == 'luxury' else 2000

    # Vintage tier bypass calculation
    if age > 20:
        return {
            "success": True,
            "brand": f"{car.brand.capitalize()} Classic",
            "year": car_year,
            "estimatedValue": f"${floor_price:,}",
            "dealMetrics": {
                "status": "fair_price",
                "label": "Vintage / Floor Value Status"
            },
            "marketInsights": {
                "averagePriceForYear": f"${floor_price:,}",
                "depreciationRate": "0% (Fully Depreciated Value Tier)",
                "mileageImpact": "Minimal (Value anchored to vehicle scrap/parts baseline)"
            }
        }

    base_price = 30000
    annual_depreciation_rate = 0.08
    mileage_penalty_per_thousand = 50

    if car.brand == 'luxury':
        base_price = 65000
        annual_depreciation_rate = 0.14
        mileage_penalty_per_thousand = 90
    elif car.brand == 'commuter':
        base_price = 26000
        annual_depreciation_rate = 0.07
        mileage_penalty_per_thousand = 40

    baseline_price_for_year = round(base_price * math.pow((1 - annual_depreciation_rate), age))

    valued_price = baseline_price_for_year

    if car.transmission == 'manual':
        valued_price = valued_price * 1.05 if car.brand == 'luxury' else valued_price * 0.93

    mileage_penalty = (car_mileage / 1000) * mileage_penalty_per_thousand
    valued_price = valued_price - mileage_penalty

    if car.condition == 'excellent': valued_price *= 1.12
    elif car.condition == 'good': valued_price *= 1.00
    elif car.condition == 'fair': valued_price *= 0.85
    elif car.condition == 'poor': valued_price *= 0.65

    final_estimate = round(max(floor_price, valued_price))

    deal_rating = "fair_price"
    deal_label = "Fair Market Price"
    
    variance_percent = (final_estimate - baseline_price_for_year) / baseline_price_for_year

    if variance_percent > 0.08:
        deal_rating = "great_deal"
        deal_label = "High-Value Asset (Excellent Condition / Low Wear)"
    elif variance_percent < -0.15:
        deal_rating = "overpriced_risk"
        deal_label = "Below Market Average (High Wear Risk)"
    # Temporary formulas end (Delete when model file is ready) ===================================================================

    return {
        "success": True,
        "brand": f"{car.brand.capitalize()} Vehicle",
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
    
    starting_price = 65000 if car.brand == 'luxury' else 26000
    if car.condition == 'excellent': starting_price *= 1.12
    elif car.condition == 'poor': starting_price *= 0.65
    
    if car.transmission == 'manual':
        starting_price = starting_price * 1.05 if car.brand == 'luxury' else starting_price * 0.93

    decay_factor = 0.82 if car.brand == 'luxury' else 0.90 
    mileage_labels = ["10k mi", "30k mi", "50k mi", "70k mi", "90k mi", "110k mi+"]
    
    depreciation_prices = []
    for index, _ in enumerate(mileage_labels):
        step_penalty = math.pow(decay_factor, index)
        baseline_floor = 4000 if car.brand == 'luxury' else 2000
        calculated_step = round(max(baseline_floor, starting_price * step_penalty))
        depreciation_prices.append(calculated_step)
    # Temporary formulas end (Delete when model file is ready) ===================================================================

    return {
        "success": True,
        "mileageLabels": mileage_labels,
        "depreciationPrices": depreciation_prices
    }