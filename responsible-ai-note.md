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
chunks and never speculate. If the chunks don't contain the answer, the model is told to
reply with an exact phrase:

> "I couldn't find this in the loaded documents."

This is enforced by prompting, not by code, so it is not a guarantee. The model usually
obeys, but it can occasionally misread a chunk, append a citation to the "not found"
message, or answer confidently from a chunk that only looks relevant.
Human verification against the cited page is always recommended.

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
- Several loaded documents cover overlapping guideline versions, so answers may blend
  them. Check which document an answer cites.