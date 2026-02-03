from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Day 2 – FastAPI validation started 🚀"}

@app.post("/predict")
def predict(request: PredictRequest):
    return {
        "input_text": request.text,
        "prediction": "success"
    }
