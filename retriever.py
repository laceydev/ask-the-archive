# retriever.py
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from config import (
    GROQ_MODEL, CHROMA_COLLECTION,
    CHROMA_PATH, TOP_K
)

load_dotenv()

SYSTEM_PROMPT = """You are a document assistant for a Singapore organisation.
Answer questions using ONLY the context provided below.
If the answer is not in the context, say exactly:
"I couldn't find this in the loaded documents."
Never speculate beyond what the documents say.
Always end your answer with the source document name and
page number in square brackets like [Document: filename.pdf, Page: 3].

Context:
{context}

Conversation so far:
{history}

Question:
{question}"""

def format_docs(docs):
    return "\n\n".join(
        f"[Source: {doc.metadata.get('source', 'Unknown')}, Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
        for doc in docs
    )

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

def build_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    
    # Simple chain: prompt → llm → parse. Retrieval happens manually in ask()
    chain = prompt | llm | StrOutputParser()
    
    return {"chain": chain, "retriever": retriever}
    return {"chain": chain, "retriever": retriever}

def ask(chain_dict, question: str, history: list) -> dict:
    history_text = ""
    if history:
        for t in history[-3:]:
            history_text += f"User: {t['user']}\nAssistant: {t['assistant']}\n"

    chain = chain_dict["chain"]
    retriever = chain_dict["retriever"]

    docs = retriever.invoke(question)
    sources = []
    for doc in docs:
        meta = doc.metadata
        entry = f"{meta.get('source', 'Unknown')}, Page {meta.get('page', '?')}"
        if entry not in sources:
            sources.append(entry)

    answer = chain.invoke({
        "question": question,
        "history": history_text,
        "context": format_docs(docs)
    })

    if not answer or answer.strip() == "":
        answer = "I couldn't find this in the loaded documents."

    return {"answer": answer, "sources": sources}