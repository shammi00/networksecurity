from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH

from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
from scipy.stats import ks_2samp
import os, sys
import pandas as pd


class DataValidation:
    def __init__(self, data_validation_config: DataValidationConfig, 
                 data_ingestion_artifact: DataIngestionArtifact):
        
        try:
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.schema_config= read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        """
        This function reads the data from the file path
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def validate_number_of_columns(self, dataframe: pd.DataFrame)-> bool:
        """
        This function validates the number of columns in the dataframe
        """
        try:
            number_of_columns = len(self.schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Dataframe has columns: {dataframe.shape[1]}")
            if dataframe.shape[1] == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def validate_number_of_numerical_columns(self, dataframe: pd.DataFrame)-> bool:
        """
        This function validates the number of numerical columns in the dataframe
        """
        try:
            numerical_columns = len(self.schema_config["numerical_columns"])
            logging.info(f"Required numerical columns: {numerical_columns}")
            logging.info(f"Numerical columns in dataframe: {dataframe.select_dtypes(include='number').shape[1]}")
            if numerical_columns == dataframe.select_dtypes(include='number').shape[1]:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def detect_data_drift(self, base_dataframe: pd.DataFrame, current_dataframe: pd.DataFrame, threshold = 0.05)-> bool:
        """
        This function detects data drift in the train and test dataframe
        """
        try:
            status = True
            reporting_dict = {}
            for column in base_dataframe.columns:
                d1 = base_dataframe[column]
                d2 = current_dataframe[column]
                p_value = ks_2samp(d1, d2).pvalue
                if threshold < p_value:
                    is_found = False
                else:
                    logging.info(f"Data drift detected in column: {column}")
                    is_found = True
                    status = False
                
                reporting_dict[column] = {
                    "p_value": float(p_value),
                    "drift_status": is_found            
                    }   
                
                # reporting_dict.update({
                #     column: {
                #         "p_value": p_value,
                #         "drift_status": is_found
                #     }                })
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            #CREATE DIRECTORY
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)


            write_yaml_file(file_path=drift_report_file_path, content=reporting_dict)

            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e


    def initialize_data_validation(self)-> DataValidationArtifact:
         
        """
        This function initiates the data validation process
        Returns:
            DataValidationArtifact: DataValidationArtifact
        """
        try:
            training_file_path = self.data_ingestion_artifact.train_file_path
            testing_file_path = self.data_ingestion_artifact.test_file_path

            # read the data from the file path
            train_dataframe = DataValidation.read_data(training_file_path)
            test_dataframe = DataValidation.read_data(testing_file_path)

            # validate the number of columns in the train and test dataframe
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                logging.error("Number of columns in the dataframe is not equal to the required number of columns")
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                logging.error("Number of columns in the dataframe is not equal to the required number of columns")

            # validate the number of numerical columns in the train and test dataframe
            status = self.validate_number_of_numerical_columns(dataframe=train_dataframe)
            if not status:
                logging.error("Number of numerical columns in the dataframe is not equal to the required number of columns")
            status = self.validate_number_of_numerical_columns(dataframe=test_dataframe)
            if not status:
                logging.error("Number of numerical columns in the dataframe is not equal to the required number of columns")

            # lets check for data drift in the train and test dataframe
            status = self.detect_data_drift(base_dataframe=train_dataframe, current_dataframe=test_dataframe)
            if status:
                dir_path = os.path.dirname(self.data_validation_config.valid_data_train_file_path)
                os.makedirs(dir_path, exist_ok=True)
                train_dataframe.to_csv(self.data_validation_config.valid_data_train_file_path, index = False, header = True)
                test_dataframe.to_csv(self.data_validation_config.valid_data_test_file_path, index = False, header = True)

            else:
                dir_path = os.path.dirname(self.data_validation_config.invalid_data_train_file_path)
                os.makedirs(dir_path, exist_ok=True)
                train_dataframe.to_csv(self.data_validation_config.invalid_data_train_file_path, index = False, header = True)
                test_dataframe.to_csv(self.data_validation_config.invalid_data_test_file_path, index = False, header = True)
            
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_data_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_data_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_data_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_data_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact
                
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
          

        