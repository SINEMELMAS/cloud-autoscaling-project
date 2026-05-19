import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "model/random_forest_cloud_autoscaling_model.pkl"

TRAFFIC_COLS = [
    "flow_byts_s",
    "flow_pkts_s",
    "src2dst_packets",
    "dst2src_packets",
    "totlen_fwd_pkts",
    "totlen_bwd_pkts",
    "bidirectional_packets"
]


def load_model():
    model = joblib.load(MODEL_PATH)
    return model


def calculate_traffic_load(df):
    df = df.copy()

    for col in TRAFFIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["traffic_load"] = (
        df["flow_byts_s"].fillna(0) * 0.40 +
        df["flow_pkts_s"].fillna(0) * 0.30 +
        df["bidirectional_packets"].fillna(0) * 0.20 +
        (
            df["src2dst_packets"].fillna(0) +
            df["dst2src_packets"].fillna(0)
        ) * 0.10
    )

    df["traffic_load"] = df["traffic_load"].replace([np.inf, -np.inf], np.nan)
    df["traffic_load"] = df["traffic_load"].fillna(0)

    return df