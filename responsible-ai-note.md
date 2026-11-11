# Responsible AI Note

AskTheArchive is a portfolio project demonstrating retrieval-augmented generation (RAG) 
for Singapore compliance documents (or just documents in general!). This note outlines its limitations and appropriate use.

## What this tool is
A document assistant that retrieves and summarises information from a 
pre-loaded set of publicly available Singapore government and regulatory documents.

## What this tool is not
- Legal advice
- A substitute for reading the actual documents
- A compliance certification tool
- Guaranteed to be accurate or complete

## How hallucination is mitigated
The system prompt explicitly instructs the model to answer ONLY from retrieved document 
chunks. If retrieved chunks don't contain relevant information, the system returns a 
hardcoded string:

"I couldn't find this in the loaded documents."

This fallback is a hardcoded string, not AI-generated, so the model cannot fabricate 
a polite-sounding excuse or just make something up.

However, the LLM can still misinterpret or misrepresent retrieved chunks. 
Human verification against source documents is always recommended, especially with important documents

## Data and privacy
- No personal data is collected or stored
- Document chunks are stored locally in ChromaDB on your machine
- Questions are sent to Groq's API for inference so do not enter confidential 
  or personal information in queries
- All source documents are publicly available from Singapore government websites

## Appropriate use
- Research and exploration of Singapore regulatory frameworks
- Quick reference during document review
- Portfolio demonstration of RAG architecture

## Not appropriate for
- Making actual compliance decisions without human review
- Replacing qualified legal or data protection advice
- Processing confidential client or organisational data

## Source documents
All documents loaded into this system are publicly available from:
- pdpc.gov.sg
- moh.gov.sg  
- csa.gov.sg
- mom.gov.sg

## Limitations
- Optimised for specific questions, not full document summarisation
- Answer quality depends on chunk retrieval; if the right chunk isn't retrieved, 
  the answer will be wrong or absent
- No guarantee of completeness— the document may contain relevant information 
  in a chunk that wasn't retrieved
- Model knowledge cutoff may affect interpretation of recent regulatory changes 