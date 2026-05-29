
import mlflow

# mlflow.set_tracking_uri("http://127.0.0.1:5000")

import dagshub

dagshub.init(repo_owner='shammi00', repo_name='networksecurity', mlflow=True)
print(mlflow.get_tracking_uri())

# runs_df = mlflow.search_runs(order_by=["start_time DESC"], max_results=20)
# print(runs_df.columns.tolist())
import pandas as pd
import numpy as np

runs_df = mlflow.search_runs(max_results=20)

print("NaN count:")
print(runs_df.isna().sum().sort_values(ascending=False).head(20))

import numpy as np

runs_df = mlflow.search_runs(order_by=["start_time DESC"], max_results=20)

print("Any NaN:", runs_df.isna().any().any())
print("Any INF:", np.isinf(runs_df.select_dtypes(include="number")).any().any())


# import dagshub
# from mlflow.tracking import MlflowClient

# dagshub.init(
#     repo_owner="shammi00",
#     repo_name="networksecurity",
#     mlflow=True
# )

# client = MlflowClient()

# try:
#     client.restore_experiment("0")
#     print("RESTORE SUCCESS")
# except Exception as e:
#     print("RESTORE FAILED")
#     print(e)

# import dagshub
# from mlflow.tracking import MlflowClient

# dagshub.init(
#     repo_owner="shammi00",
#     repo_name="networksecurity",
#     mlflow=True
# )

# client = MlflowClient()

# for exp in client.search_experiments(view_type=3):
#     print(exp.experiment_id, exp.name, exp.lifecycle_stage)