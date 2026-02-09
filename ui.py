import streamlit as st
import requests

st.title("PDF RAG Chat")

uploaded = st.file_uploader("Upload PDF")

if uploaded:
    r = requests.post(
        "http://127.0.0.1:8000/upload",
        files={"file": uploaded}
    )
    st.success("PDF Uploaded & Indexed")

question = st.text_input("Ask question")

if st.button("Ask"):
    res = requests.post(
        "http://127.0.0.1:8000/ask",
        params={"question": question}
    )

    st.write(res.json()["answer"])
