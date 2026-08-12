# Network Security Project - Phishing Detection

## Project Overview

This is an end-to-end machine learning project focused on network security, specifically designed for phishing detection. The solution demonstrates a comprehensive ML workflow from data processing through model training to cloud deployment.

![Phishing Detection](https://img.shields.io/badge/ML-Phishing%20Detection-blue)
![MLOps](https://img.shields.io/badge/MLOps-AWS%20Deployment-orange)
![Status](https://img.shields.io/badge/Status-Production--Ready-green)

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Model Pipeline](#model-pipeline)
- [Deployment Infrastructure](#deployment-infrastructure)
- [Performance Metrics](#performance-metrics)
- [MLOps Features](#mlops-features)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Automated ML Pipeline**: Complete workflow from data ingestion to model deployment.
- **Drift Detection**: Monitoring for data quality and model performance changes.
- **MLflow Integration**: Experiment logging and model versioning.
- **CI/CD Pipeline**: Automated linting, testing, and deployment via GitHub Actions.
- **Cloud Deployment**: Dockerized solution deployed on AWS.
- **API Endpoint**: FastAPI-based endpoints for real-time prediction.
- **Preprocessing Pipeline**: KNNImputer-based data transformation.
- **Extensive Model Training**: Multiple classifiers with hyperparameter tuning and evaluation.

## Architecture

```
                                ┌───────────────────┐
                                │                   │
                                │   Data Sources    │
                                │   (MongoDB)       │
                                │                   │
                                └────────┬──────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Data Pipeline                           │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────────┐  │
│  │ Ingestion    │───▶|  Validation  │───▶│ Transformation   │  │
│  └──────────────┘     └──────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Model Training Pipeline                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Training     │───▶│ Evaluation   │───▶│ Model Selection │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Deployment Pipeline                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Docker       │───▶│ AWS ECR      │───▶│ FastAPI Service │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

## Installation

### Prerequisites
- Python 3.11
- Docker
- AWS CLI
- MongoDB

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/4ashutosh98/end-to-end-ml-project-mlflow-aws.git
   cd end-to-end-ml-project-mlflow-aws
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**

   Create a `.env` file with:
   ```
   MONGO_DB_URL = <your_mongodb_connection_string>
   AWS_ACCESS_KEY_ID = <your_aws_access_key>
   AWS_SECRET_ACCESS_KEY = <your_aws_secret_key>
   AWS_REGION = <your_preferred_region>
   DAGSHUB_TOKEN = <your_dagshub_token>
   ```

4. **Install in Development Mode**
   ```bash
   pip install -e .
   ```

## Project Structure

```
end-to-end-ml-project-mlflow-aws/
│
├── .github/workflows/           # CI/CD configurations
├── artifacts/                   # Training and validation artifacts
├── final_model/                 # Serialized model and preprocessors
├── networksecurity/             # Main package
│   ├── components/              # Core components
│   │   ├── data_ingestion.py    # Data ingestion logic
│   │   ├── data_transformation.py  # Preprocessing pipelines
│   │   ├── data_validation.py   # Data quality checks
│   │   └── model_trainer.py     # Model training and evaluation
│   ├── constant/                # Constant definitions
│   ├── entity/                  # Data classes for configurations and artifacts
│   ├── exception/               # Custom exception handling
│   ├── logging/                 # Logging configuration
│   ├── pipeline/                # Pipeline orchestration
│   └── utils/                   # Utility functions
├── templates/                   # API templates
├── app.py                       # FastAPI application
├── Dockerfile                   # Docker configuration
├── README.md                    # Project documentation
├── requirements.txt             # Dependencies list
└── setup.py                     # Setup script
```

## Data Pipeline

### Data Ingestion
- Reads raw data from CSV files.
- Splits data into training and testing sets, saving them as numpy arrays.

### Data Validation
- Verifies data quality and schema.
- Performs drift detection using statistical tests.
- Generates detailed validation reports.

### Data Transformation
- **Preprocessing:**
  - Uses KNNImputer with parameters from configuration:
    ```python
    KNNImputer(**DATA_TRANSFORMER_IMPUTER_PARAMS)
    ```
  - Builds a scikit-learn Pipeline for data imputation.
- **Transformation:**
  - Applies transformation on training and testing datasets.
  - Replaces target value -1 with 0.
  - Concatenates transformed features with target columns:
    ```python
    train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
    ```
- **Saving Artifacts:**
  - Saves numpy arrays and preprocessor pipeline objects:
    ```python
    save_object("final_model/preprocessor.pkl", preprocessor_object)
    ```

## Model Pipeline

### Model Training
Trains multiple classifiers with hyperparameter tuning:

- **LogisticRegression**
  ```python
  "C": [0.1, 1, 10]
  ```
- **KNeighborsClassifier**
  ```python
  "n_neighbors": [3, 5, 7, 9],
  "weights": ["uniform", "distance"]
  ```
- **DecisionTreeClassifier**
  ```python
  "criterion": ["gini", "entropy", "log_loss"],
  "splitter": ["best", "random"],
  "max_depth": [None, 5, 10, 15, 20, 25, 30],
  "max_features": ["sqrt", "log2"],
  "min_samples_split": [2, 5, 10]
  ```
- **AdaBoostClassifier**
  ```python
  "n_estimators": [8, 16, 32, 64, 128, 256],
  "learning_rate": [0.001, 0.01, 0.05, 0.1]
  ```
- **GradientBoostingClassifier**
  ```python
  "loss": ["log_loss", "exponential"],
  "learning_rate": [0.001, 0.01, 0.05, 0.1],
  "n_estimators": [8, 16, 32, 64, 128, 256],
  "criterion": ["friedman_mse", "squared_error"],
  "max_features": ["sqrt", "log2"],
  "subsample": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
  ```
- **RandomForestClassifier**
  ```python
  "n_estimators": [8, 16, 32, 64, 128, 256],
  "criterion": ["gini", "entropy", "log_loss"],
  "max_features": ["sqrt", "log2"],
  "max_depth": [None, 5, 10, 15, 20, 25, 30]
  ```
- **XGBoostClassifier**
  ```python
  "n_estimators": [8, 16, 32, 64, 128, 256],
  "learning_rate": [0.001, 0.01, 0.05, 0.1],
  "max_depth": [3, 5, 7, 9],
  "subsample": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
  ```

### Model Selection & Evaluation
- Evaluates each model using custom metrics (precision, recall, F1-score).
- Selects the best model based on evaluation scores.
- Tracks training and testing metrics via MLflow:
  ```python
  mlflow.log_metric("f1_score", f1_score)
  mlflow.sklearn.log_model(best_model, "model")
  ```
- Combines best model and preprocessor into a `NetworkModel` class for inference.
- Saves the final model artifact:
  ```python
  save_object("final_model/model.pkl", best_model)
  ```

## Deployment Infrastructure

### Containerization and CI/CD
- **Docker:** Builds container images for consistent deployment.
- **GitHub Actions:** Implements CI/CD pipeline for linting, testing, building, and deployment.
- **AWS:** Pushes Docker images to AWS ECR and deploys through a self-hosted runner.

### API Service
- **FastAPI:** Hosts APIs for training and prediction endpoints.
- **Endpoints:**
  - `GET /train` to initiate training.
  - `POST /predict` for real-time phishing detection.

## Performance Metrics

The project leverages standard classification metrics:
- **Precision:** Accuracy of positive predictions.
- **Recall:** Ability to identify all positive instances.
- **F1-Score:** Balanced metric combining precision and recall.

All metrics are logged via MLflow for model performance tracking.

## MLOps Features

- **Experiment Tracking:** MLflow integration for end-to-end experiment history.
- **Model Registry:** Versioned storage of trained models.
- **DagsHub Integration:** Collaborative experiment tracking.
- **Data Drift Monitoring:** Continuous monitoring of incoming data quality.
- **Reproducibility:** Fixed seeds and versioned dependencies ensure reproducibility.
- **Automation:** Fully automated pipeline from training to deployment.

## API Reference

### Training Endpoint
```
GET /train
```
- Initiates the model training process.
- Returns training status and metrics.

### Prediction Endpoint
```
POST /predict
```
- Accepts uploaded data for prediction.
- Returns prediction results with confidence scores.

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add amazing feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request for review.

## License

Distributed under the MIT License. See `LICENSE` for more details.