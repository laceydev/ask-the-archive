# app.py
import streamlit as st
from pathlib import Path
from retriever import build_chain, ask
from config import DOCS_FOLDER, CHROMA_PATH
import threading

st.set_page_config(page_title="AskTheArchive", page_icon="🗂️")


def load_css(file_name: str):
    css_path = Path(__file__).parent / file_name
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("style.css")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("Ask The Archive")
    st.divider()
    st.markdown("**Loaded documents:**")
    docs = list(Path(DOCS_FOLDER).glob("*.pdf")) + list(Path(DOCS_FOLDER).glob("*.md"))
    if docs:
        for doc in docs:
            st.markdown(f"{doc.name}")
            st.divider()
    else:
        st.warning("No documents found in /docs")
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

# ---------- Model loading with jokes ----------
if "chain_dict" not in st.session_state:
    holder = {}
    done = threading.Event()

    jokes = [
        ("Indexing your documents... this might take a minute...or several", "I don't trust Matlab developers, They're always plotting something!"),
        ("Embedding vectors...", "Why do programmers prefer dark mode? Because light attracts bugs!!"),
        ("still going!! A bittt more", "Why was the JavaScript developer sad? Because he didn't Node how to Express himself :("),
        ("Almost there...", "Which Hogwarts house is able to communicate securely? SSLytheryn"),
        ("Almost there...", "Why aren't frontend developers humble? They display: flex;!!"),
        ("Almost there...", "A GET request was reluctant to go the party... They had no body to go with!"),
        ("Finishing up...", "I walked down a street where the houses were numbered 64K, 128K, 256K, 512K and 1MB. It was a nice trip down memory lane"),
        ("Finishing up...", "I once knew an excellent programmer that believed they wrote bad spaghetti code. They had Impasta Syndrome."),
    ]

    def load():
        try:
            if not Path(CHROMA_PATH).exists():
                from ingest import ingest_all
                ingest_all()
            holder["chain_dict"] = build_chain()
        except Exception as e:
            holder["error"] = e
        finally:
            done.set()

    threading.Thread(target=load, daemon=True).start()

    status = st.empty()
    joke_display = st.empty()
    i = 0
    while not done.is_set():
        status.info(jokes[i % len(jokes)][0])
        joke_display.markdown(f"*{jokes[i % len(jokes)][1]}*")
        i += 1
        done.wait(timeout=5)

    status.empty()
    joke_display.empty()

    if "error" in holder:
        st.error("Something went wrong loading the documents. Try refreshing.")
        st.stop()
    st.session_state.chain_dict = holder["chain_dict"]

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Header ----------
st.markdown("# ASK THE ARCHIVE")
st.markdown(
    "<p class='subtitle'>Ask your documents anything!</p>",
    unsafe_allow_html=True,
)

# ---------- Chat history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.markdown(f"- {s}")

# ---------- Chat input ----------
if question := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            result = ask(
                st.session_state.chain_dict,
                question,
                st.session_state.history,
            )
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.markdown(f"- {s}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
    st.session_state.history.append({
        "user": question,
        "assistant": result["answer"],
    })