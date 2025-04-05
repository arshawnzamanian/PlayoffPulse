from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

app = FastAPI()

@app.get("/predict")
def predict_top_teams():
    return {"message": "Prediction logic goes here (WIP)"}
