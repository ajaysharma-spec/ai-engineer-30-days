from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
model = SentenceTransformer("all-MiniLM-L6-v2")

# Chroma
client = chromadb.Client()
collection = client.get_or_create_collection(name="pdf_rag")

# -------- PDF UPLOAD --------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    reader = PdfReader(file.file)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Simple chunking
    chunks = [text[i:i+800] for i in range(0, len(text), 800)]

    embeds = model.encode(chunks).tolist()

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeds[i]],
            ids=[f"{file.filename}_{i}"],
            metadatas=[{
                "filename": file.filename,
                "chunk_id": i
            }]
        )

    return {"status": "pdf running"}

# -------- ASK QUESTION --------

@app.post("/ask")
async def ask(question: str):

    q_embed = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=q_embed,
        n_results=1
    )

    answer = results["documents"][0][0]
    source = results["metadatas"][0][0]

    return {
        "answer": answer,
        "source": source
    }