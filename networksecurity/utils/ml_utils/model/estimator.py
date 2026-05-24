import sys
import pandas as pd
import mlflow.pyfunc
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class NetworkModel(mlflow.pyfunc.PythonModel):
    def __init__(self, preprocessor_obj, model_obj): 
        try:
            self.preprocessor_obj = preprocessor_obj
            self.model_obj = model_obj
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def predict(self,context=None, model_input=None ):
        try:
            if model_input is None:
                model_input=context
            X_transformed = self.preprocessor_obj.transform(model_input)
            return self.model_obj.predict(X_transformed)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e