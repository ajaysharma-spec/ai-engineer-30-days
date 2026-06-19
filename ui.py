import streamlit as st
import requests

st.title("PDF RAG Chat")

# Upload PDF
uploaded = st.file_uploader("Upload PDF")

if uploaded:
    res = requests.post(
        "http://127.0.0.1:8000/upload",
        files={"files": uploaded}
    )
    st.write(res.json())

# Ask question
question = st.text_input("Ask question")

if st.button("Ask"):
    res = requests.post(
        "http://127.0.0.1:8000/ask?question=" + question
    )

    data = res.json()
    st.write(data)

    if "answer" in data:
        st.write("Answer:", data["answer"])