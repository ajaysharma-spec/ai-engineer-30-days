from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import os
from chromadb.config import Settings


app = FastAPI()

# OpenRouter API key from ENV
API_KEY = os.getenv("OPENROUTER_API_KEY")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client(
    settings=Settings(anonymized_telemetry=False)
)

collection = client.create_collection(name="pdf_docs")

def call_llm(context, question):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "pdf-rag"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": f"Answer using only this context:\n{context}"},
            {"role": "user", "content": question}
        ]
    }

    r = requests.post(url, headers=headers, json=data)

    print("RAW RESPONSE:", r.text)

    return r.json()["choices"][0]["message"]["content"]

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    chunks = text.split("\n")

    embeddings = model.encode(chunks).tolist()

    for i, c in enumerate(chunks):
        collection.add(
            documents=[c],
            embeddings=[embeddings[i]],
            ids=[str(i)]
        )

    return {"status": "PDF indexed"}

@app.post("/ask")
async def ask(question: str):
    q_embed = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=q_embed,
        n_results=1
    )

    context = results["documents"][0][0]

    answer = call_llm(context, question)

    return {
        "question": question,
        "answer": answer
    }
