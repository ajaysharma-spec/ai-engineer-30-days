import streamlit as st
import requests

st.title("AI Chatbot")

API_URL = "http://127.0.0.1:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Type your message")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    response = requests.post(
        API_URL,
        json={"message": user_input}
    )

    bot_reply = response.json()["reply"]

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])