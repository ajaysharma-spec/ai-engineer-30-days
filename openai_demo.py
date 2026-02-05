import requests

API_KEY = "YOUR_API_KEY"


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
        {"role": "user", "content": "Explain FastAPI in one sentence"}
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json())
