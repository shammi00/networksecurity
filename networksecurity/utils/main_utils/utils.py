import yaml
import os, sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import numpy as np
# import dill
import pickle

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score


def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.
    
    Args:
        file_path (str): The path to the YAML file.
    
    Returns:
        dict: The contents of the YAML file as a dictionary.
    """
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """
    Writes a dictionary to a YAML file.
    
    Args:
        file_path (str): The path to the YAML file.
        content (dict): The dictionary to write to the YAML file.
        replace (bool): Whether to replace the file if it already exists. Default is False.

    Returns:
        None
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as yaml_file:
            yaml.safe_dump(content, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def save_numpy_array_data(file_path: str, array: np.array) -> None:
    """
    Saves a numpy array to a file.
    
    Args:
        file_path (str): The path to the file where the array will be saved.
        array (np.array): The numpy array to save.

    Returns:
        None
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path: str, obj: object) -> None:
    """
    Saves a Python object to a file using pickle.
    
    Args:
        file_path (str): The path to the file where the object will be saved.
        obj (object): The Python object to save.

    Returns:
        None
    """
    try:
        logging.info("Entered the save_object method of MainUtils class")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path: str) -> object:
    """
    Loads a Python object from a file using pickle.
    
    Args:
        file_path (str): The path to the file from which the object will be loaded.

    Returns:
        object: The Python object loaded from the file.
    """
    try:
        if not os.path.exists(file_path):
            raise NetworkSecurityException(f"The file {file_path} does not exist", sys)
        logging.info("Entered the load_object method of MainUtils class")
        with open(file_path, "rb") as file_obj:
            obj = pickle.load(file_obj)
        logging.info("Exited the load_object method of MainUtils class")
        return obj
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path: str) -> np.array:
    """
    Loads a numpy array from a file.
    
    Args:
        file_path (str): The path to the file from which the array will be loaded.

    Returns:
        np.array: The numpy array loaded from the file.
    """
    try:
        if not os.path.exists(file_path):
            raise NetworkSecurityException(f"The file {file_path} does not exist", sys)
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
        

# method 1

# def evaluate_models(X_train, y_train, X_test, y_test, models, params) -> dict:
#     """
#     This function evaluates the models on the given data and returns the metrics
#     X_train : np.array : training data
#     y_train : np.array : training target
#     X_test : np.array : testing data
#     y_test : np.array : testing target
#     models : dict : dictionary of models
#     params : dict : dictionary of parameters
#     return : dict : dictionary of metrics
#     """
#     try:
#         report = {}
#         for i in range(len(list(models.keys()))):
#             model = list(models.values())[i]
#             model_params = params[list(models.keys())[i]]

#             gs = GridSearchCV(model, model_params, cv=3, verbose=1, n_jobs=-1)
#             gs.fit(X_train, y_train)

#             model.set_params(**gs.best_params_)
#             model.fit(X_train, y_train) 

#             y_train_pred = model.predict(X_train)

#             y_test_pred = model.predict(X_test)

#             train_model_score = r2_score(y_train, y_train_pred)
#             test_model_score = r2_score(y_test, y_test_pred)

#             report[list(models.keys())[i]] = test_model_score
#         return report

#     except Exception as e:
#         raise NetworkSecurityException(e, sys) from e
    
# method 2
def evaluate_models(X_train, y_train, X_test, y_test, models, params) -> dict:
    """
        This function evaluates the models on the given data and returns the metrics
        X_train : np.array : training data
        y_train : np.array : training target
        X_test : np.array : testing data
        y_test : np.array : testing target
        models : dict : dictionary of models
        params : dict : dictionary of parameters
        return : dict : dictionary of metrics
    """
    try:

        report = {}
        
        for model_name, model in models.items():
                para=params[model_name]
    
                # hyperparameter tuning
                gs = GridSearchCV(model, para, cv=3, verbose=1, n_jobs=-1)
                gs.fit(X_train, y_train)
    
                # update model with best parameters
                model.set_params(**gs.best_params_)
                # train final model
                model.fit(X_train, y_train)
                # predict training data
                y_train_pred = model.predict(X_train)
                # predict testing data
                y_test_pred = model.predict(X_test)
                # train and test model score
                train_model_score = r2_score(y_train, y_train_pred)
                test_model_score = r2_score(y_test, y_test_pred)
                # save the best model score in report dictionary
                report[model_name] = test_model_score

                return report

    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
