# cloud-autoscaling-project
````markdown
# ML-Based Cloud Auto-Scaling Simulator Using ONE-MS-I Microservice Traffic Dataset

## Project Overview

This project is a machine learning based cloud auto-scaling simulator developed using the ONE-MS-I micro-services based network traffic dataset.

The main purpose of the project is to simulate how a cloud system can dynamically adjust server resources according to network traffic intensity and anomaly risk. The system uses a trained Random Forest machine learning model to predict whether a network traffic record is normal or anomalous. Then, it calculates a traffic load score and recommends the required number of cloud servers.

The final application is deployed as a FastAPI service on Render and provides API endpoints for prediction and auto-scaling simulation.

## Project Title

ML-Based Cloud Auto-Scaling Simulator Using ONE-MS-I Microservice Traffic Dataset

## Dataset

The dataset used in this project is:

ONE-MS-I: A micro-services based network traffic dataset

Dataset source:

https://ieee-dataport.org/documents/one-ms-i-micro-services-based-network-traffic-dataset

The ONE-MS-I dataset is designed for cloud-native and microservice-based environments. It contains network traffic collected from a micro-services oriented PPDR application called Mobitrust. The traffic was collected using NFStream and includes features compatible with CIC-IDS2017-style network flow analysis.

## Dataset Structure

The dataset contains multiple scenario folders such as:

```text
1h
2h
4h
6h
8h
1h+1h
2h+2h
4h+4h
6h+6h
8h+8h
````

Each scenario contains five microservices:

```text
monitor
message
gateway
postgresql
orchestrator
```

Each microservice folder contains:

```text
training.csv
data.csv
```

In this project:

* `data.csv` files were used as the main dataset for machine learning and simulation.
* `training.csv` files were kept as normal traffic reference data.
* Each row was enriched with `scenario`, `service`, and `source` metadata.
* All `data.csv` files were combined into a single dataset.
* The final machine learning datasets were saved as:

  * `train_final.csv`
  * `validation_final.csv`
  * `test_final.csv`

## Project Objectives

The objectives of this project are:

1. To analyze microservice network traffic data.
2. To train a machine learning model for normal/anomaly traffic prediction.
3. To calculate traffic load from network flow features.
4. To classify traffic intensity as Low, Medium, or High.
5. To recommend the required number of cloud servers.
6. To expose the system through FastAPI endpoints.
7. To deploy the system on a cloud platform using Render.

## System Architecture

The project workflow is:

```text
ONE-MS-I Dataset
        |
        v
Data Preprocessing
        |
        v
Feature Selection
        |
        v
Random Forest ML Model
        |
        v
Normal / Anomaly Prediction
        |
        v
Traffic Load Calculation
        |
        v
Low / Medium / High Traffic Classification
        |
        v
Cloud Server Recommendation
        |
        v
FastAPI Service
        |
        v
Render Cloud Deployment
```

## Machine Learning Model

The machine learning model used in this project is:

```text
Random Forest Classifier
```

The model predicts whether a traffic record is:

```text
0 = Normal Traffic
1 = Anomaly Traffic
```

Several machine learning models were tested during development. Although Gradient Boosting achieved strong validation performance, Random Forest was selected for the final implementation because it provides a good balance between performance, interpretability, and deployment simplicity.

## Train, Validation, and Test Split

The dataset was split based on traffic scenarios instead of random splitting. This approach helps evaluate whether the model can generalize to unseen traffic scenarios.

The final split was:

```python
train_scenarios = [
    "1h", "2h", "4h", "6h", "8h",
    "1h+1h", "2h+2h"
]

validation_scenarios = [
    "4h+4h"
]

test_scenarios = [
    "6h+6h", "8h+8h"
]
```

Final dataset sizes:

```text
Train shape:      596,587 records
Validation shape: 130,432 records
Test shape:       392,920 records
```

## Model Performance

The Random Forest model achieved the following results on the final test set:

```text
Accuracy:  0.9999414639
Precision: 0.9987630966
Recall:    0.9995630962
F1-score:  0.9991629363
ROC-AUC:   0.9999998662
```

Confusion Matrix:

```text
[[379170     17]
 [     6  13727]]
```

These results show that the model performed very well on the scenario-based test set.

## Traffic Load Calculation

After anomaly prediction, a traffic load score was calculated using selected network flow features:

```text
flow_byts_s
flow_pkts_s
src2dst_packets
dst2src_packets
totlen_fwd_pkts
totlen_bwd_pkts
bidirectional_packets
```

The traffic load formula used in this project is:

```python
traffic_load = (
    flow_byts_s * 0.40 +
    flow_pkts_s * 0.30 +
    bidirectional_packets * 0.20 +
    (src2dst_packets + dst2src_packets) * 0.10
)
```

The calculated traffic load was classified into three levels:

```text
Low Traffic
Medium Traffic
High Traffic
```

The classification was performed using quantile-based thresholds.

## Cloud Auto-Scaling Logic

The cloud auto-scaling decision system combines:

1. Traffic intensity
2. ML-based anomaly prediction
3. Anomaly probability

The server recommendation logic is:

| Condition         | Recommended Servers | Decision                 |
| ----------------- | ------------------: | ------------------------ |
| Low traffic       |                   1 | Low Traffic - Scale Down |
| Medium traffic    |                   2 | Medium Traffic - Stable  |
| High traffic      |                   3 | High Traffic - Scale Up  |
| High anomaly risk |                   4 | Security Risk - Scale Up |

A traffic record is treated as high security risk if:

```text
predicted_anomaly = 1
anomaly_probability >= 0.80
```

## Auto-Scaling Simulation Results

The final simulation on the test set produced the following server distribution:

```text
1 server: 119,362 records
2 servers: 126,248 records
3 servers: 133,585 records
4 servers: 13,725 records
```

Scaling decision distribution:

```text
High Traffic - Scale Up:     133,585
Medium Traffic - Stable:     126,248
Low Traffic - Scale Down:    119,362
Security Risk - Scale Up:     13,725
```

Average recommended servers by microservice:

```text
monitor:       2.431360
gateway:       2.356814
postgresql:    2.186640
orchestrator:  1.982906
message:       1.743036
```

Average recommended servers by scenario:

```text
8h+8h: 2.123591
6h+6h: 2.084886
```

## FastAPI Deployment

The trained Random Forest model was integrated into a FastAPI application.

The API provides the following endpoints:

```text
GET /
GET /predict-sample
GET /simulate
```

## API Endpoints

### Root Endpoint

```text
GET /
```

Returns a basic message showing that the API is running.

Example response:

```json
{
  "message": "ML-Based Cloud Auto-Scaling Simulator is running.",
  "endpoints": [
    "/simulate",
    "/predict-sample"
  ]
}
```

### Predict Sample Endpoint

```text
GET /predict-sample
```

This endpoint selects one traffic record from the sample test data and returns:

* predicted anomaly class
* anomaly probability
* traffic load value

Example response:

```json
{
  "predicted_anomaly": 0,
  "anomaly_probability": 0,
  "traffic_load": 1.8000000000000003,
  "note": "0 means Normal traffic, 1 means Anomaly traffic."
}
```

### Simulate Endpoint

```text
GET /simulate
```

This endpoint runs the auto-scaling simulation on 1000 sample traffic records.

Example response:

```json
{
  "total_records": 1000,
  "normal_predictions": 963,
  "anomaly_predictions": 37,
  "server_distribution": {
    "1": 300,
    "2": 324,
    "3": 339,
    "4": 37
  },
  "scaling_decision_distribution": {
    "High Traffic - Scale Up": 339,
    "Medium Traffic - Stable": 324,
    "Low Traffic - Scale Down": 300,
    "Security Risk - Scale Up": 37
  },
  "average_recommended_servers": 2.113,
  "average_anomaly_probability": 0.03711581847236569
}
```

## Project Structure

```text
cloud-autoscaling-project
│
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── model_utils.py
│   └── scaler.py
│
├── data
│   └── sample_test_data.csv
│
├── model
│   └── random_forest_cloud_autoscaling_model.pkl
│
├── requirements.txt
├── runtime.txt
└── README.md
```

## Main Files

### app/main.py

Contains the FastAPI application and API endpoints.

### app/model_utils.py

Loads the trained machine learning model and calculates traffic load.

### app/scaler.py

Contains the traffic classification and server recommendation logic.

### model/random_forest_cloud_autoscaling_model.pkl

The trained Random Forest model.

### data/sample_test_data.csv

A sample dataset used by the API for simulation.

## Installation and Local Usage

Clone the repository:

```bash
git clone https://github.com/SINEMELMAS/cloud-autoscaling-project.git
cd cloud-autoscaling-project
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI application:

```bash
python -m uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Requirements

The project uses the following main dependencies:

```text
fastapi
uvicorn
pandas
numpy
joblib
scikit-learn==1.6.1
```

The scikit-learn version is fixed because the trained model was saved with scikit-learn 1.6.1. Using a different version may cause model loading errors.

## Render Deployment

The project was deployed on Render as a Python Web Service.

Render settings:

```text
Runtime: Python
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The `runtime.txt` file is used to specify the Python version:

```text
python-3.11.9
```

## Cloud Computing Relevance

This project demonstrates several cloud computing concepts:

* Microservice traffic analysis
* Cloud resource scaling
* Auto-scaling decision logic
* ML-based anomaly-aware resource management
* FastAPI-based cloud service
* Render cloud deployment
* API-based simulation

The project simulates how a cloud platform can use machine learning and traffic analysis to dynamically adjust resources based on workload and security risk.

## Results Summary

The deployed system successfully performs the following tasks:

1. Loads a trained Random Forest model.
2. Predicts normal or anomalous network traffic.
3. Calculates traffic load.
4. Classifies traffic as Low, Medium, or High.
5. Recommends the required number of cloud servers.
6. Returns cloud auto-scaling decisions through API endpoints.
7. Runs successfully in a cloud environment using Render.

## Citation

If using the ONE-MS-I dataset, cite the original dataset publication:

```text
Tomas, P.R., Felix, P., Rosa, L., Gomes, A.S., Cordeiro, L. (2024).
A Novel Approach for Continual and Federated Network Anomaly Detection.
In: Arai, K. (eds) Proceedings of the Future Technologies Conference (FTC) 2024, Volume 4.
FTC 2024. Lecture Notes in Networks and Systems, vol 1157.
Springer, Cham.
https://doi.org/10.1007/978-3-031-73128-0_14
```

Dataset page:

```text
https://ieee-dataport.org/documents/one-ms-i-micro-services-based-network-traffic-dataset
```


