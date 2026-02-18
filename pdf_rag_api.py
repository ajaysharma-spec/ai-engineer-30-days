from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import requests
import os

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

docs = []


def call_llm(context, question):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": f"Answer using this info:\n{context}"},
            {"role": "user", "content": question}
        ]
    }

    r = requests.post(url, headers=headers, json=payload)

    return r.json()["choices"][0]["message"]["content"]


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    docs.append(text)

    return {"status": "PDF stored"}


@app.post("/ask")
async def ask(question: str):

    context = docs[-1] if docs else ""

    answer = call_llm(context, question)

    return {
        "question": question,
        "answer": answer
    }

