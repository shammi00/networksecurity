import os
import sys
import pandas as pd

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact


from networksecurity.utils.main_utils.utils import save_object , load_object 
from networksecurity.utils.main_utils.utils import load_numpy_array_data , evaluate_models
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score   

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)

import mlflow
from urllib.parse import urlparse
from mlflow.models import infer_signature
import dagshub



class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    @staticmethod  
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def track_mlflow(self, network_model, train_df, classification_train_metric, classification_test_metric ):
        dagshub.init(repo_owner='shammi00', repo_name='networksecurity', mlflow=True)
        # mlflow.set_tracking_uri("http://127.0.0.1:5000")
        # mlflow.set_tracking_uri("file:./mlruns")
        # mlflow.set_tracking_uri("sqlite:///mlflow.db")
        # mlflow.set_tracking_uri("sqlite:///E:/Network%20Security/mlflow.db")
        print(mlflow.get_tracking_uri())

        mlflow.set_experiment("NetworkSecurity")
        with mlflow.start_run():
            # train metrics
            f1_score = classification_train_metric.f1_score
            recall_score = classification_train_metric.recall_score
            precision_score = classification_train_metric.precision_score

            mlflow.log_metric("train_f1_score", f1_score)
            mlflow.log_metric("train_precision_score", precision_score)
            mlflow.log_metric("train_recall_score", recall_score)

            # test metrics
            f1_score = classification_test_metric.f1_score
            recall_score = classification_test_metric.recall_score
            precision_score = classification_test_metric.precision_score

            mlflow.log_metric("test_f1_score", f1_score)
            mlflow.log_metric("test_precision_score", precision_score)
            mlflow.log_metric("test_recall_score", recall_score)

            # Generate model signature for proper schema tracking
            sample_input = train_df.iloc[:5, :-1]  # Sample input for signature (excluding target column)
            predictions = network_model.predict(sample_input)
            signature = infer_signature(sample_input, predictions)

            # Check if we're using a tracking server that supports Model Registry
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
            
            # Log the model with proper registration if not using file store
            if tracking_url_type_store not in ["", "file"]:

                mlflow.pyfunc.log_model(
                    name="model",
                    python_model=network_model,
                    signature=signature,
                    registered_model_name="NetworkSecurityModel",
                    input_example=sample_input
                )

            else:

                mlflow.pyfunc.log_model(
                    name="model",
                    python_model=network_model,
                    signature=signature,
                    input_example=sample_input
                )

    def train_model(self, x_train, y_train, x_test, y_test) -> ModelTrainerArtifact:
        try:
            models = {
                "Logistic Regression": LogisticRegression(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(verbose=1),
                "AdaBoost Classifier": AdaBoostClassifier(),
                "Gradient Boosting Classifier": GradientBoostingClassifier(verbose=1)
            }

            params={
                "Decision Tree": {
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                
                    'max_features':['sqrt','log2',None],
                    # 'n_estimators': [8,16,32,64,128,256]
                },
                "Gradient Boosting":{
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate':[.1,.01,.05,.001],
                    # 'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Logistic Regression":{},
                "AdaBoost Classifier":{
                    'learning_rate':[.1,.01,0.5,.001],
                    'loss':['linear','square','exponential'],
                    # 'n_estimators': [8,16,32,64,128,256]
                }
                
            }

            model_report: dict = evaluate_models(X_train=x_train, y_train=y_train, X_test=x_test, y_test=y_test,
                                                 models=models,params=params)
            # method 1
            #  to get the best model score from dict
            # best_model_score = max(sorted(model_report.values()))

            # to get the best model name from dict
            # best_model_name = list(model_report.keys())[
            #     list(model_report.values()).index(best_model_score)
            # ]
            
            # method 2
            # best_model_name = max(model_report, key=model_report.get)
            # best_model_score = model_report[best_model_name]

            # method 3
            """to get the best model name and best model score from dict"""
            best_model_name, best_model_score = max(model_report.items(), key=lambda x: x[1])

            best_model = models[best_model_name]
            
            if best_model_score < self.model_trainer_config.expected_score:
                raise NetworkSecurityException("No best model found with score greater than the expected score")
            
            print(f"Best Model Found, Model Name: {best_model_name}, Model Score: {best_model_score}")
            
            preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
            
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)
            network_model = NetworkModel(
                preprocessor_obj=preprocessor, 
                model_obj=best_model
            )
            save_object(self.model_trainer_config.trained_model_file_path, network_model)
            save_object("final_model/model.pkl", best_model)
            # predict on training and testing data to get classification metrics
            y_train_pred = best_model.predict(x_train)
            classification_train_metric = get_classification_score(y_train, y_train_pred)

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_test, y_test_pred)

            train_dataframe = self.data_transformation_artifact.valid_train_file_path
            train_df= pd.read_csv(train_dataframe)

            
            
            self.track_mlflow(network_model,train_df,classification_train_metric,classification_test_metric)

            
            
            #ModelTrainerArtifact class to store model trainer artifacts
            model_traine_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )
            logging.info(f"Model Trainer Artifact: {model_traine_artifact}")
            return model_traine_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    def initialize_model_trainer(self) -> ModelTrainerArtifact:
        
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            train_array = load_numpy_array_data(train_file_path)
            test_array = load_numpy_array_data(test_file_path)
            
            X_train, y_train = train_array[:,:-1], train_array[:,-1]
            X_test, y_test = test_array[:,:-1], test_array[:,-1]

            model_trainer_artifact = self.train_model(X_train, y_train , X_test, y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
           
        