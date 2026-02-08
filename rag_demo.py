import chromadb
from sentence_transformers import SentenceTransformer
import requests

API_KEY = "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"

# 1. Embedding model load
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Vector DB (Chroma)
client = chromadb.Client()
collection = client.create_collection(name="docs")

# 3. Sample documents (apna bhi add kar sakte ho)
docs = [
    "FastAPI is a Python framework for building APIs.",
    "SQL is used to store structured data in tables.",
    "RAG means Retrieval Augmented Generation."
]

# 4. Documents → embeddings
embeddings = model.encode(docs).tolist()

# 5. Store in Chroma
for i, d in enumerate(docs):
    collection.add(
        documents=[d],
        embeddings=[embeddings[i]],
        ids=[str(i)]
    )

print("Documents stored.")

# 6. User question
query = "What is FastAPI?"

query_embedding = model.encode([query]).tolist()

# 7. Retrieve most relevant doc
results = collection.query(
    query_embeddings=query_embedding,
    n_results=1
)

context = results["documents"][0][0]
print("Retrieved:", context)

# 8. Send context + question to LLM
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "ai-engineer-roadmap"
}

data = {
    "model": "mistralai/mistral-7b-instruct",
    "messages": [
        {"role": "system", "content": f"Use this info to answer: {context}"},
        {"role": "user", "content": query}
    ]
}

resp = requests.post(url, headers=headers, json=data)

print("\nFinal AI Answer:")
print(resp.json()["choices"][0]["message"]["content"])
