import os

import requests
import streamlit as st
from dotenv import load_dotenv

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8001/query")
load_dotenv()
st.set_page_config(page_title="Chat with Retrieval", layout="wide")
st.title("🔍 Chat with Contextual Retrieval")

# 🧪 Debug mode toggle
debug_mode = st.sidebar.checkbox("Show Debug Info", value=False)

# 🧠 Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 💬 Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 📥 User input
query = st.chat_input("Ask a question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    payload = {
        "query": query,
        "top_k": 3
    }

    try:
        response = requests.post(API_ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()

        answer = data.get("answer", "No answer returned.")
        contexts = data.get("contexts", [])
        relevant_texts = data.get("relevant_texts", [])

        with st.chat_message("assistant"):
            st.markdown(f"**Answer:** {answer}")

            if contexts:
                st.markdown("**Retrieved Contexts:**")
                for i, ctx in enumerate(contexts, 1):
                    st.markdown(f"> **[{i}]** {ctx}")

            if debug_mode and relevant_texts:
                st.markdown("---")
                st.markdown("🛠️ **Debug Info: Relevant Texts**")
                for i, item in enumerate(relevant_texts, 1):
                    text = item.get("text", "")
                    score = item.get("score", "N/A")
                    meta = item.get("meta", {})
                    st.markdown(f"**[{i}]** `{text}`\n- Score: `{score}`")
                    for key, val in meta.items():
                        st.markdown(f"  - {key}: `{val}`")

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"**Answer:** {answer}"
        })

    except Exception as e:
        error_msg = f"⚠️ Error: {e}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})