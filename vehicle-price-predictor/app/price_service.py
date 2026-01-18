import os
import sys
import datetime
import numpy as np
import pandas as pd
import joblib

# Set up path for scraping modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Import GPT scraping utilities
from scraping.gpt_scraper import get_gpt_summary_riyasewana, get_gpt_summary_ikman

# Load ML model
MODEL_PATH = os.path.join(BASE_DIR, "models", "price_predictor_xgb.pkl")
model_pipeline = joblib.load(MODEL_PATH)


def predict_price_ml(brand, model, year, location, conditions=None):
    """
    Predict vehicle price using XGBoost model with all relevant fields.
    """
    try:
        current_year = datetime.datetime.now().year
        vehicle_age = current_year - int(year)

        # Base input
        features = {
            'brand': brand,
            'model': model,
            'year': int(year),
            'location': location or "Colombo",
            'vehicle_age': vehicle_age
        }

        # Include condition fields if passed
        if conditions:
            features.update({
                'paint_condition': conditions.get("paint_condition"),
                'engine_condition': conditions.get("engine_condition"),
                'tire_condition': conditions.get("tire_condition"),
                'scratches_dents': conditions.get("scratches_dents"),
                'facelift': conditions.get("facelift"),
                'mileage': float(conditions.get("mileage", 0)) or 0,
                'fuel_efficiency': float(conditions.get("fuel_efficiency", 0)) or 0,
                'service_records': conditions.get("service_records"),
                'interior_condition': conditions.get("interior_condition")
            })

        df = pd.DataFrame([features])

        # Make prediction (log-transformed model)
        log_price = model_pipeline.predict(df)[0]
        predicted_price = round(float(np.expm1(log_price)), 2)
        return predicted_price

    except Exception as e:
        return f"ML Prediction Error: {str(e)}"


def predict_price_gpt(brand, model, year):
    """
    Use GPT to summarize live scraped vehicle price data.
    """
    try:
        riyasewana_summary, avg_riyasewana = get_gpt_summary_riyasewana(brand, model, year)
        ikman_summary, avg_ikman = get_gpt_summary_ikman(brand, model, year)

        return {
            "riyasewana": {
                "summary": riyasewana_summary,
                "average_price": avg_riyasewana
            },
            "ikman": {
                "summary": ikman_summary,
                "average_price": avg_ikman
            }
        }
    except Exception as e:
        return {
            "error": f"GPT Scraping Error: {str(e)}"
        }