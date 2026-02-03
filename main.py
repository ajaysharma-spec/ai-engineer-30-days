from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Day 1 of AI Engineer roadmap 🚀"}

@app.post("/predict")
def predict(data: dict):
    return {
        "input": data,
        "prediction": "success"
    }
