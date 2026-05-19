from fastapi import FastAPI
import pandas as pd

from app.model_utils import load_model, calculate_traffic_load
from app.scaler import (
    classify_traffic_level,
    decide_server_count,
    scaling_decision
)

app = FastAPI(
    title="ML-Based Cloud Auto-Scaling Simulator",
    description="Random Forest based anomaly-aware cloud auto-scaling simulator using ONE-MS-I microservice traffic dataset.",
    version="1.0"
)

model = load_model()


@app.get("/")
def home():
    return {
        "message": "ML-Based Cloud Auto-Scaling Simulator is running.",
        "endpoints": ["/simulate", "/predict-sample"]
    }


@app.get("/simulate")
def simulate():
    df = pd.read_csv("data/sample_test_data.csv")

    if "target" in df.columns:
        X = df.drop(columns=["target"])
    else:
        X = df.copy()

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    result = df.copy()
    result["predicted_anomaly"] = predictions
    result["anomaly_probability"] = probabilities

    result = calculate_traffic_load(result)

    low_threshold = result["traffic_load"].quantile(0.33)
    high_threshold = result["traffic_load"].quantile(0.66)

    result["traffic_level"] = result["traffic_load"].apply(
        lambda x: classify_traffic_level(x, low_threshold, high_threshold)
    )

    result["recommended_servers"] = result.apply(
        lambda row: decide_server_count(
            row["traffic_level"],
            row["predicted_anomaly"],
            row["anomaly_probability"]
        ),
        axis=1
    )

    result["scaling_decision"] = result.apply(
        lambda row: scaling_decision(
            row["traffic_level"],
            row["predicted_anomaly"],
            row["anomaly_probability"]
        ),
        axis=1
    )

    summary = {
        "total_records": int(len(result)),
        "normal_predictions": int((result["predicted_anomaly"] == 0).sum()),
        "anomaly_predictions": int((result["predicted_anomaly"] == 1).sum()),
        "server_distribution": result["recommended_servers"].value_counts().sort_index().to_dict(),
        "scaling_decision_distribution": result["scaling_decision"].value_counts().to_dict(),
        "average_recommended_servers": float(result["recommended_servers"].mean()),
        "average_anomaly_probability": float(result["anomaly_probability"].mean())
    }

    return summary


@app.get("/predict-sample")
def predict_sample():
    df = pd.read_csv("data/sample_test_data.csv")
    sample = df.sample(1, random_state=42)

    if "target" in sample.columns:
        X = sample.drop(columns=["target"])
    else:
        X = sample.copy()

    predicted_anomaly = int(model.predict(X)[0])
    anomaly_probability = float(model.predict_proba(X)[:, 1][0])

    sample_result = calculate_traffic_load(sample)

    traffic_load = float(sample_result["traffic_load"].iloc[0])

    return {
        "predicted_anomaly": predicted_anomaly,
        "anomaly_probability": anomaly_probability,
        "traffic_load": traffic_load,
        "note": "0 means Normal traffic, 1 means Anomaly traffic."
    }