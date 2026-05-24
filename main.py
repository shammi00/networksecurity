from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import ( 
    DataIngestionConfig, 
    TrainingPipelineConfig, 
    DataValidationConfig, 
    DataTransformationConfig,
    ModelTrainerConfig
)

import sys

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion=DataIngestion(data_ingestion_config)
        logging.info("Starting data ingestion")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        print(data_ingestion_artifact)
        logging.info("Data ingestion completed successfully")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(data_validation_config, data_ingestion_artifact)
        logging.info("Starting data validation")
        data_validation_artifact = data_validation.initialize_data_validation()
        print(data_validation_artifact)
        logging.info("Data validation completed successfully")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation=DataTransformation(data_transformation_config, data_validation_artifact)
        logging.info("Starting data transformation")
        data_transformation_artifact = data_transformation.initialize_data_transformation_pipeline()
        print(data_transformation_artifact)
        logging.info("Data transformation completed successfully")
        logging.info("Model Training started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config, data_transformation_artifact)
        model_trainer_artifact = model_trainer.initialize_model_trainer()
        logging.info(f"Model Training completed successfully")
    except Exception as e:
        logging.error(f"Error occurred: {e}")  # Log the error!
        raise NetworkSecurityException(e, sys) from e