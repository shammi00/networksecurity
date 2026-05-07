import yaml
import os, sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import numpy as np
# import dill
import pickle


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