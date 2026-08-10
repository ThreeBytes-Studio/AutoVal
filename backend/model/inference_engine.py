import joblib
import pandas as pd
from pydantic import BaseModel
from pathlib import Path
from fastapi import FastAPI

app = FastAPI()

# Import model
MODEL_PATH = Path(__file__).resolve().parent / "car_price_pipeline.joblib"
model = joblib.load(MODEL_PATH)

# Defines expected data from frontend
class PredictionInput(BaseModel):
    year: int
    manufacturer: str 
    model: str
    condition: str | None = None
    cylinders: str | None = None
    fuel: str
    odometer: float
    title_status: str
    transmission: str
    drive: str | None = None
    size: str | None = None
    type: str | None = None

@app.post("/predict")
def predict(data: PredictionInput) -> dict:
    # Convertion process:
    # JSON -> Python Object -> Dictionary -> DataFrame
    user_input = pd.DataFrame([data.model_dump()])

    # Joblib includes a pipeline of data preprocessing and model itself
    result = model.predict(user_input)

    # Receives numpy float value
    # Convert the prediction to a JSON-friendly response
    return {
        "msg": "success!",
        "prediction": float(result[0])
        }
