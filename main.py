from fastapi import FastAPI, UploadFile, File
import os

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = None

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 🔹 Extract text
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

# 🔹 Chunk text
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_text(text)
    chunks = [c.strip() for c in chunks if c.strip()]
    return chunks

# 🔹 Upload API
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global db

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)

    if not text or not text.strip():
        return {"error": "No readable text found"}

    chunks = chunk_text(text)

    if not chunks:
        return {"error": "No chunks created"}

    db = Chroma.from_texts(chunks, embedding)

    return {
        "message": "PDF processed successfully",
        "chunks": len(chunks)
    }

# 🔹 Ask API (FINAL WORKING)
@app.post("/ask")
async def ask_question(query: str):
    global db

    if db is None:
        return {"error": "Upload PDF first"}

    docs = db.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Answer based only on this context:

    {context}

    Question: {query}
    """

    # 🔥 DIRECT KEY (NO ENV ISSUE)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="your api key"
    )

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    return {
        "question": query,
        "answer": answer
    }