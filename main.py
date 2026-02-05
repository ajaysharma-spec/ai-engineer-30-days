import requests
from fastapi import FastAPI
from pydantic import BaseModel

API_KEY = "YOUR_API_KEY"


app = FastAPI()

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(req: PredictRequest):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "ai-engineer-roadmap"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": req.text}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    return {
        "answer": response.json()["choices"][0]["message"]["content"]
    }
