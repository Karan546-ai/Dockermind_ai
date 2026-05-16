# 🧠 DocMind AI — Intelligent Document Chat

A high-performance, asynchronous backend for **Retrieval-Augmented Generation (RAG)** built with FastAPI.
Upload PDF documents, which are parsed, chunked, and indexed into a vector store for **real-time, context-aware chat responses**.

---

## ✨ Features

* **Multi-File PDF Upload:** Asynchronously upload multiple PDF documents at once.
* **Advanced Document Parsing:** Uses Google's Gemini API for high-quality, structure-aware parsing of PDFs into Markdown.
* **Vectorization & Indexing:**

  * Employs OpenAI's `text-embedding-3-small` model for efficient embedding generation.
  * Uses **Qdrant** as the vector store.
* **Real-time Indexing Status:** Provides real-time feedback on the document indexing pipeline.
* **Streaming Chat Responses:** Chat answers from OpenAI's GPT-4.1 are delivered as a real-time stream.
* **Scalable Architecture:** Clean, class-based, and dependency-injected code for scalability and testability.
* **Simple Test UI:** Includes a basic HTML/JS interface for quick testing.

---

## 📂 Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── router.py               # Main API router
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── chat.py         # /chat endpoint logic
│   │           ├── document.py     # /uploadfiles & /indexing_status endpoints
│   │           └── health.py       # /health endpoint logic
│   ├── config/
│   │   └── settings.py             # Environment variables & settings
│   ├── schemas/
│   │   ├── chat.py                 # Pydantic schema for chat requests
│   │   └── document.py             # Pydantic schemas for document responses
│   ├── server.py                   # FastAPI app entry point & CORS config
│   └── services/
│       ├── chat_service.py         # Core RAG chat logic
│       ├── document_service.py     # PDF parsing and chunking logic
│       ├── embedding_service.py    # Embedding generation
│       └── vector_store_service.py # Qdrant interaction
├── requirements.txt                # Project dependencies
└── testing-UI/
    └── index.html                  # Simple frontend for testing
```

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Document Parsing:** Google Gemini API
* **LLM for Chat:** OpenAI GPT-4.1
* **Embeddings:** OpenAI `text-embedding-3-small`
* **Vector Store:** Qdrant
* **Python Libraries:**
  `uvicorn`, `pydantic`, `python-multipart`, `google-genai`, `openai`, `qdrant-client`, `llama-index-core`

---

## 🚀 Setup and Installation

### 1. Create a Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file by copying the template:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# API Keys
GEMINI_API_KEY="your_google_gemini_api_key"
OPENAI_API_KEY="your_openai_api_key"
LLAMA_CLOUD_API_KEY="your_llama_cloud_api_key"

# Model Configuration
GEMINI_MODEL=gemini-2.5-pro
OPENAI_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSION=1536

# Qdrant Configuration 
QDRANT_URL="your_qdrant_url"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_COLLECTION=documents
```

---

## ▶️ Running the Application

Run the FastAPI server:

```bash
uvicorn app.server:app --reload
```

The server will be available at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🎛️ How to Use

1. **Open** `testing-UI/index.html` in your browser.
2. **Upload Files:**

   * Click "Choose File" and select one or more PDF documents.
   * Click **"Upload and Index"**.
3. **Monitor Progress:**

   * Progress bars show real-time indexing status.
4. **Chat:**

   * When all files show "Completed," the chat box becomes active.
   * Ask questions based on uploaded documents.

---

## 🔗 API Endpoints

All endpoints are prefixed with `/api/v1/`.

| Method | Endpoint                      | Description                                | Response                                             |
| ------ | ----------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| GET    | `/health`                     | Checks if the API server is running        | `{ "status": "ok" }`                                 |
| POST   | `/uploadfiles`                | Upload one or more PDF files for indexing  | `[{"index_id": str, "filename": str}]`               |
| GET    | `/indexing_status/{index_id}` | Status of a specific indexing job          | `{ "index_id": str, "status": str, "details": str }` |
| POST   | `/chat`                       | Submit a query, receive streaming response | `StreamingResponse (text/plain)`                     |

---
