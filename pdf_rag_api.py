from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import os

app = FastAPI()

# ================= SECURITY ==================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_SECRET = os.getenv("API_SECRET")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ================= CORS =====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= EMBEDDINGS ==============

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

# ================= LLM ======================

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

# ================= PDF UPLOAD ==============

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

# ================= ASK ======================

@app.post("/ask")
async def ask(question: str, x_api_key: str = Header(None)):

    verify_api_key(x_api_key)

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