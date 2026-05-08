import os,sys
import numpy as np
import pandas as pd

"""
defining common constants variables for training pipeline

"""
TARGET_COLUMN: str = "Result"
PIPELINE_NAME: str = "Network_Security"
ARTIFACT_DIR: str = "artifact"
FILE_NAME: str = "PhisingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

SCHEMA_FILE_PATH: str = os.path.join("data_schema", "schema.yaml")

"""
Data Ingestion related constant starts with DATA_INGESTION VAR NAMEES

"""
DATA_INGESTION_COLLECTION_NAME: str = "NetworkData"
DATA_INGESTION_DATABASE_NAME: str = "shammi"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

"""
Data Validation related constant starts with DATA_VALIDATION VAR NAMEES

"""
DATA_VALIDATION_DIR_NAME : str = "data_validation"
DATA_VALIDATION_VALID_DIR : str = "validated"
DATA_VALIDATION_INVALID_DIR : str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR : str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME : str = "report.yaml"

"""
Data Transformation related constant starts with DATA_TRANSFORMATION VAR NAMEES

"""
DATA_TRANSFORMATION_DIR_NAME : str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DIR : str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR : str = "transformed_object"
PREPROCESSING_OBJECT_FILE_NAME: str="preprocessing.pkl"

# knn imputer to handle missing values in the dataset
DATA_TRANSFORMER_IMPUTER_PARAMS : dict = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}