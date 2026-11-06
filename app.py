# app.py
import streamlit as st
from pathlib import Path
from retriever import build_chain, ask
from config import DOCS_FOLDER

st.set_page_config(page_title="AskTheArchive", page_icon="🗂️")

with st.sidebar:
    st.title("🗂️ AskTheArchive")
    st.markdown("---")
    st.markdown("**Loaded documents:**")
    docs = list(Path(DOCS_FOLDER).glob("*.pdf")) + list(Path(DOCS_FOLDER).glob("*.md"))
    if docs:
        for doc in docs:
            st.markdown(f" {doc.name}")
    else:
        st.warning("No documents found in /docs")
    st.markdown("---")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "chain_dict" not in st.session_state:
    with st.spinner("Loading documents and model..."):
        st.session_state.chain_dict = build_chain()

st.title("Ask your documents anything.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.markdown(f"- {s}")

if question := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            result = ask(
                st.session_state.chain_dict,
                question,
                st.session_state.history
            )
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.markdown(f"- {s}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"]
    })
    st.session_state.history.append({
        "user": question,
        "assistant": result["answer"]
    })