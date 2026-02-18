from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import requests
import os

app = FastAPI()

# 🔐 Load API key safely from Render Environment Variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 📌 Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 📦 Simple in-memory storage (Render safe)
documents = []
embeddings_store = []


# ==============================
# 🔹 LLM Call (OpenRouter)
# ==============================
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
            {
                "role": "system",
                "content": f"Answer using this context:\n{context}"
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("RAW RESPONSE:", response.text)

    data = response.json()

    if "choices" not in data:
        return "LLM Error: " + str(data)

    return data["choices"][0]["message"]["content"]


# ==============================
# 🔹 Upload PDF
# ==============================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    reader = PdfReader(file.file)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    chunks = text.split("\n")

    embeds = model.encode(chunks).tolist()

    documents.extend(chunks)
    embeddings_store.extend(embeds)

    return {"status": "PDF uploaded and indexed"}


# ==============================
# 🔹 Ask Question
# ==============================
@app.post("/ask")
async def ask(question: str):

    if not documents:
        return {"error": "No PDF uploaded yet."}

    q_embed = model.encode([question])[0]

    scores = []
    for emb in embeddings_store:
        score = sum(a * b for a, b in zip(q_embed, emb))
        scores.append(score)

    best_index = scores.index(max(scores))
    context = documents[best_index]

    answer = call_llm(context, question)

    return {
        "question": question,
        "answer": answer
    }

