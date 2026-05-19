def classify_traffic_level(traffic_load, low_threshold, high_threshold):
    if traffic_load <= low_threshold:
        return "Low"
    elif traffic_load <= high_threshold:
        return "Medium"
    else:
        return "High"


def decide_server_count(traffic_level, predicted_anomaly, anomaly_probability):
    if predicted_anomaly == 1 and anomaly_probability >= 0.80:
        return 4
    elif traffic_level == "High":
        return 3
    elif traffic_level == "Medium":
        return 2
    else:
        return 1


def scaling_decision(traffic_level, predicted_anomaly, anomaly_probability):
    if predicted_anomaly == 1 and anomaly_probability >= 0.80:
        return "Security Risk - Scale Up"
    elif traffic_level == "High":
        return "High Traffic - Scale Up"
    elif traffic_level == "Medium":
        return "Medium Traffic - Stable"
    else:
        return "Low Traffic - Scale Down"