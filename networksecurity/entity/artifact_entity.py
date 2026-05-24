from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    """DataIngestionArtifact class to store data ingestion artifacts"""
    train_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifact:
    """DataValidationArtifact class to store data validation artifacts"""
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str   
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str
    feature_names: list


@dataclass
class DataTransformationArtifact:
    """DataTransformationArtifact class to store data transformation artifacts"""
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str
    valid_train_file_path: str

@dataclass
class ClassificationMetricArtifact:
    """ClassificationMetricArtifact class to store classification metric artifacts"""
    #accuraracy_score: float
    precision_score: float
    recall_score: float
    f1_score: float
@dataclass
class ModelTrainerArtifact:
    """ModelTrainerArtifact class to store model trainer artifacts"""
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact