# 📄 PDF RAG Chatbot (FastAPI + Chroma + LLM)

This project is a production-style GenAI backend that allows users to upload a PDF and ask questions based on its content using Retrieval Augmented Generation (RAG).

## 🚀 Features

- FastAPI backend
- PDF upload
- Text embeddings using Sentence Transformers
- Vector storage with ChromaDB
- Similarity search
- LLM-based answering
- Swagger UI for testing

## 🧠 Architecture

PDF → Embeddings → Chroma Vector DB → Similarity Search → LLM → Answer

## 🛠 Tech Stack

- Python
- FastAPI
- ChromaDB
- Sentence Transformers
- OpenRouter LLM API

## ▶ How to Run

```bash
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn chromadb sentence-transformers pypdf python-multipart requests
uvicorn pdf_rag_api:app --reload
