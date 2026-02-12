# PDF RAG Chatbot

AI-powered PDF Question Answering System using Retrieval-Augmented Generation (RAG).

---

## 🚀 Features
- Upload PDF files
- Extract text automatically
- Convert text into embeddings
- Store embeddings in ChromaDB
- Ask questions about PDF
- LLM generates contextual answers
- Simple Streamlit Chat UI

---

## 🧠 Tech Stack
- Python
- FastAPI
- Sentence Transformers
- ChromaDB
- Streamlit
- OpenRouter API

---

## ⚙️ Installation

### 1️⃣ Create Virtual Environment
python -m venv venv

### 2️⃣ Activate
venv\Scripts\activate

### 3️⃣ Install Requirements
pip install -r requirements.txt

---

## ▶️ Run Backend
uvicorn pdf_rag_api:app --reload

Open:
http://127.0.0.1:8000/docs

---

## ▶️ Run Frontend
streamlit run ui.py

Open:
http://localhost:8501

---

## 🔄 Project Workflow

PDF → Text Extraction → Embeddings → ChromaDB → LLM → Answer

---

## 👨‍💻 Author
Ajay Sharma
