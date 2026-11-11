# ingest.py
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import (
    CHUNK_SIZE, CHUNK_OVERLAP,
    CHROMA_COLLECTION, CHROMA_PATH, DOCS_FOLDER
)

load_dotenv()

def ingest_all():
    docs_path = Path(DOCS_FOLDER)
    all_docs = []

    print("Loading documents...")

    for filepath in docs_path.iterdir():
        suffix = filepath.suffix.lower()
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(filepath))
                docs = loader.load()
                all_docs.extend(docs)
                print(f"  Loaded: {filepath.name} ({len(docs)} pages)")
            elif suffix == ".md":
                loader = TextLoader(str(filepath), encoding="utf-8")
                docs = loader.load()
                all_docs.extend(docs)
                print(f"  Loaded: {filepath.name}")
        except Exception as e:
            print(f"  Skipped {filepath.name}: {e}")

    if not all_docs:
        print("No documents found in /docs. Add PDFs or markdown files and try again.")
        return

    print(f"\nSplitting {len(all_docs)} pages into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(all_docs)
    print(f"Created {len(chunks)} chunks.")

    print("\nEmbedding and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Wipe and recreate
    import shutil
    if Path(CHROMA_PATH).exists():
        shutil.rmtree(CHROMA_PATH)
        print("Cleared existing ChromaDB store.")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION,
        persist_directory=CHROMA_PATH
    )

    print(f"\nDone! {len(chunks)} chunks stored in ChromaDB.")
    print("You can now run: streamlit run app.py")

if __name__ == "__main__":
    ingest_all()