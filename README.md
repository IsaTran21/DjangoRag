## RAG Workflow Implementation

A Retrieval-Augmented Generation (RAG) system built with **LangChain** and **LangGraph**, using **ChromaDB** for vector storage and retrieval.

### Features
- Backend developed with **Django** and **Django REST Framework** to provide API endpoints and handle data processing.
- Frontend built using **HTML**, **CSS**, and **JavaScript**.
- PDF parsing with page-limit controls and throttling to prevent abuse or brute-force uploads.
- Integrated **LlamaParse** and **Unstructured** for efficient PDF text extraction.
- Advanced prompt engineering combined with document retrieval for strong contextual understanding.
- **Plotly.js** visualization for tracking input and output token counts (including system tokens).
### Set environment variables
Need to set the environment variables, named "DJANGO_LLM" and "OPENAI"
### Implementation
```
pip instal -r requirements.txt
```
After that, run the server (this is for development mode):
```
python manage.py runserver
```
