from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OPENROUTER_API_KEY ="API KEY"

# conversation memory
chat_history = []

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):

    chat_history.append({
        "role": "user",
        "content": req.message
    })

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/auto",
            "messages": chat_history
        }
    )

    result = response.json()

    if "choices" not in result:
        return {"reply": "Error: " + str(result)}

    answer = result["choices"][0]["message"]["content"]

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return {"reply": answer}