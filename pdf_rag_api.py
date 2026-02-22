from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import os

app = FastAPI(title="PDF RAG API")

# ================= ENV =================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_SECRET = os.getenv("API_SECRET")

# ================= SECURITY =================

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

# ================= EMBEDDINGS =================

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection(name="docs")

# ================= LLM =================

def call_llm(context, question):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": f"Answer from context:\n{context}"},
            {"role": "user", "content": question}
        ]
    }

    r = requests.post(url, headers=headers, json=payload)

    print("RAW:", r.text)

    return r.json()["choices"][0]["message"]["content"]

# ================= UPLOAD =================

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    reader = PdfReader(file.file)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    chunks = text.split("\n")

    embeds = model.encode(chunks).tolist()

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeds[i]],
            ids=[str(i)]
        )

    return {"status": "PDF indexed"}

# ================= ASK =================

@app.post("/ask")
async def ask(question: str, x_api_key: str = Header(...)):

    verify_key(x_api_key)

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

# ================= ROOT =================

@app.get("/")
def home():
    return {"status": "PDF RAG API Running"}