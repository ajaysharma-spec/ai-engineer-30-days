from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import os

app = FastAPI()

# Load API Key from ENV (SAFE)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Chroma DB (simple local)
client = chromadb.Client()
collection = client.get_or_create_collection("docs")


def call_llm(context, question):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "pdf-rag"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": f"Answer using this context:\n{context}"},
            {"role": "user", "content": question}
        ]
    }

    r = requests.post(url, headers=headers, json=payload)

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

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[str(i)]
        )

    return {"status": "PDF uploaded & indexed"}


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

