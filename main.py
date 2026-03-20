from fastapi import FastAPI, UploadFile, File
import os

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global DB
db = None

# Embedding model
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Extract text
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

# Chunk text (FIXED)
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)

    # Clean chunks
    chunks = [c.strip() for c in chunks if c.strip()]

    return chunks

# Upload API
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global db

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    print("Text length:", len(text))

    if not text or not text.strip():
        return {"error": "No readable text found"}

    chunks = chunk_text(text)

    print("Chunks count:", len(chunks))

    if chunks:
        print("First chunk:", chunks[0])

    if not chunks:
        return {"error": "No chunks created"}

    db = Chroma.from_texts(chunks, embedding)

    return {
        "message": "PDF processed successfully",
        "chunks": len(chunks),
        "sample_chunk": chunks[0] if chunks else ""
    }