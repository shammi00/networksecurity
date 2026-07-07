import sys
import os

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
import numpy as np
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import load_object
import mlflow


app=FastAPI()
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates=Jinja2Templates(directory="./template")

# Mount static files for CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", tags=["dashboard"])
async def dashboard(request: Request):
    """Main dashboard page with MLflow metrics"""
    try:
    
        # Get recent runs from MLflow
        try:
            runs_df = mlflow.search_runs(order_by=["start_time DESC"], max_results=10)
            runs_df = runs_df.fillna(0)
        except Exception as mlflow_error:
            logging.warning(f"MLflow search failed: {mlflow_error}")
            runs_df = pd.DataFrame()
        
        # Get best model metrics
        best_f1 = 0
        best_precision = 0
        best_recall = 0
        
        if len(runs_df) > 0 and 'metrics.test_f1_score' in runs_df.columns:
            # Find the run with best F1 score
            best_run_idx = runs_df['metrics.test_f1_score'].idxmax()
            best_run = runs_df.loc[best_run_idx]
            best_f1 = best_run.get('metrics.test_f1_score', 0) or 0
            best_precision = best_run.get( 'metrics.test_precision_score', 0) or 0
            best_recall = best_run.get('metrics.test_recall_score', 0) or 0
        
        # Prepare data for template
        dashboard_data = {
            "total_runs": len(runs_df),
            "best_f1_score": float(best_f1),
            "best_precision": float(best_precision),
            "best_recall": float(best_recall),
            "recent_runs": runs_df.to_dict('records') if len(runs_df) > 0 else []
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "data": dashboard_data
        })
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        # Return dashboard with empty data if there's an error
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "data": {
                "total_runs": 0,
                "best_f1_score": 0.0,
                "best_precision": 0.0,
                "best_recall": 0.0,
                "recent_runs": []
            }
        })

@app.get("/api/mlflow/runs", tags=["api"])
async def get_mlflow_runs():
    """API endpoint to get MLflow runs data as JSON"""
    try:
        runs_df = mlflow.search_runs(order_by=["start_time DESC"], max_results=20)
        runs_df = runs_df.fillna(0)
        runs_df = runs_df.replace([np.inf, -np.inf], 0)
        return {"success": True, "data": runs_df.to_dict('records')}
    except Exception as e:
        logging.error(f"MLflow API error: {e}")
        return {"success": False, "error": str(e), "data": []}

@app.get("/train")
async def train_route():
    try:
        training_pipeline=TrainingPipeline()
        training_pipeline.run_pipeline()
        return Response("training is successfull")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request:Request,file:UploadFile=File(...)):
    try:
        df=pd.read_csv(file.file)
        preprocessor=load_object(file_path="final_model/preprocessor.pkl")
        model=load_object(file_path="final_model/model.pkl")
        network_model=NetworkModel(preprocessor_obj=preprocessor,model_obj=model)
        print(df.iloc[0])
        y_pred=network_model.predict(df)
        print(y_pred)
        df['predicted_column']=y_pred
        df.to_csv("output_prediction/predicted_data.csv",index=False)
        print(df['predicted_column'])
        table_html=df.to_html(classes="table table-striped")
        return templates.TemplateResponse("table.html",{"request":request,"table":table_html})

    except Exception as e:
        raise NetworkSecurityException(e,sys)


if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)