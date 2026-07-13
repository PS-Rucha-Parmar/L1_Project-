# DocAi — Automated Documentation-to-RAG Builder

> **Production-quality RAG pipeline** that crawls any official library documentation,
> converts it to structured Markdown, chunks and embeds it, stores it in a persistent
> vector database, and exposes a modern Streamlit chat UI — all from a single URL.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Pipeline Walkthrough](#pipeline-walkthrough)
   - [Crawling](#1-crawling)
   - [Cleaning & Markdown Generation](#2-cleaning--markdown-generation)
   - [Metadata](#3-metadata)
   - [Chunking](#4-chunking)
   - [Embeddings](#5-embeddings)
   - [Vector Database](#6-vector-database)
   - [Retrieval](#7-retrieval)
   - [RAG Pipeline](#8-rag-pipeline)
6. [Running the Streamlit App](#running-the-streamlit-app)
7. [Running Tests](#running-tests)
8. [Troubleshooting](#troubleshooting)
9. [Future Improvements](#future-improvements)

---

## Architecture Overview

```
Documentation URL(s)
       │
       ▼
┌──────────────┐
│   Crawler    │  Firecrawl → Crawl4AI → Trafilatura → BeautifulSoup (priority order)
└──────┬───────┘
       │ raw HTML / Markdown
       ▼
┌──────────────┐
│  Preprocessor│  Clean → Structure → Convert to Markdown → Generate metadata.json
└──────┬───────┘
       │ clean Markdown + metadata
       ▼
┌──────────────┐
│   Chunker    │  Semantic chunking → RecursiveCharacterTextSplitter fallback
└──────┬───────┘
       │ text chunks + metadata
       ▼
┌──────────────┐
│   Embedder   │  BAAI/bge-small-en-v1.5 via SentenceTransformers (batched)
└──────┬───────┘
       │ dense vectors
       ▼
┌──────────────┐
│  Vector DB   │  ChromaDB (default) or FAISS — persistent, metadata-indexed
└──────┬───────┘
       │ retriever
       ▼
┌──────────────┐
│  RAG Chain   │  LangChain + LangGraph — retrieval → prompt → LLM → citations
└──────┬───────┘
       │ answer + sources
       ▼
┌──────────────┐
│ Streamlit UI │  Chat · Source viewer · Chunk viewer · Scores · Settings
└──────────────┘
```

---

## Folder Structure

```
DocAi/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Pydantic-settings configuration singleton
│   └── logging_config.py    # Rotating file + console logging setup
├── crawler/
│   ├── __init__.py
│   └── spider.py            # Multi-strategy web crawler with retry logic
├── preprocessing/
│   ├── __init__.py
│   ├── cleaner.py           # HTML / Markdown cleaning pipeline
│   ├── chunker.py           # Semantic + RecursiveCharacterTextSplitter chunking
│   └── metadata.py          # Document metadata generator
├── embeddings/
│   ├── __init__.py
│   └── embedder.py          # Batched HuggingFace embedding pipeline
├── vectordb/
│   ├── __init__.py
│   └── vector_store.py      # Chroma & FAISS store factory + persistence helpers
├── retrieval/
│   ├── __init__.py
│   └── searcher.py          # Similarity search, MMR, Top-K, metadata filters
├── pipeline/
│   ├── __init__.py
│   └── rag_chain.py         # LangGraph RAG workflow with citation handling
├── prompts/
│   ├── __init__.py
│   └── templates.py         # All LangChain prompt templates
├── ui/
│   ├── __init__.py
│   └── app.py               # Streamlit application
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Shared utility functions
├── logs/                    # Rotating application logs (auto-created)
├── knowledge_base/          # Ingested Markdown documents + metadata.json files
│   ├── langchain/
│   ├── langgraph/
│   └── ...                  # One folder per documentation source
├── vectordb_storage/        # Persisted vector index files (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.10+
- `pip`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/docai.git
cd docai

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (required by Crawl4AI)
playwright install chromium

# 5. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and preferred settings
```

---

## Configuration

All configuration is managed through the `.env` file. See `.env.example` for the full list of variables.

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | LLM backend: `groq`, `openai`, `anthropic` |
| `LLM_MODEL` | `llama3-8b-8192` | Model identifier |
| `CRAWLER_TYPE` | `trafilatura` | Crawler backend priority |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | SentenceTransformer model |
| `VECTOR_DB_TYPE` | `chroma` | `chroma` or `faiss` |
| `CHUNK_SIZE` | `800` | Target chunk size in tokens |
| `CHUNK_OVERLAP` | `150` | Chunk overlap in tokens |
| `RETRIEVAL_TOP_K` | `5` | Chunks returned per query |
| `RETRIEVAL_METHOD` | `mmr` | `similarity` or `mmr` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Pipeline Walkthrough

### 1. Crawling

The crawler module (`crawler/spider.py`) automatically selects the highest-priority available backend:

1. **Firecrawl** — cloud-based, handles JavaScript-heavy pages.
2. **Crawl4AI** — async, Playwright-based headless browser.
3. **Trafilatura** — fast, content-focused extraction.
4. **BeautifulSoup** — reliable HTML parsing fallback.

It recursively follows internal documentation links, deduplicates URLs, skips PDFs/images/videos, retries failed pages, and maintains a full crawl log.

### 2. Cleaning & Markdown Generation

`preprocessing/cleaner.py` strips navigation bars, sidebars, footers, advertisements, JavaScript, CSS, cookie banners, and duplicate paragraphs. Each cleaned page is then converted to a standardised Markdown document with the following sections:

`# Overview` · `# Concepts` · `# Architecture` · `# Workflow` · `# API` · `# Parameters` · `# Return Values` · `# Code Example` · `# Output` · `# Notes` · `# Best Practices` · `# Common Mistakes` · `# Performance Notes` · `# Related Topics` · `# References`

Code blocks, tables, and warnings are always preserved.

### 3. Metadata

`preprocessing/metadata.py` generates a `metadata.json` beside every Markdown file containing:

```json
{
  "id": "uuid",
  "title": "Page title",
  "library": "langchain",
  "topic": "retrieval",
  "url": "https://...",
  "category": "guide",
  "tags": ["rag", "retriever"],
  "word_count": 342,
  "reading_time": "2 min",
  "created": "2024-01-01T00:00:00Z",
  "updated": "2024-01-01T00:00:00Z",
  "embedding_status": "pending"
}
```

### 4. Chunking

`preprocessing/chunker.py` applies **semantic chunking first**, falling back to `RecursiveCharacterTextSplitter` (chunk size 800, overlap 150). Code blocks, tables, lists, and examples are never split mid-structure.

### 5. Embeddings

`embeddings/embedder.py` uses `BAAI/bge-small-en-v1.5` via SentenceTransformers. Documents are processed in configurable batches with progress logging. Embeddings are automatically persisted to the vector database.

### 6. Vector Database

`vectordb/vector_store.py` wraps both **ChromaDB** (default) and **FAISS** (optional) behind a unified interface. Indexes are persisted to `vectordb_storage/` on every write.

### 7. Retrieval

`retrieval/searcher.py` supports:
- **Similarity Search** — cosine distance ranking.
- **MMR (Maximal Marginal Relevance)** — balances relevance and diversity.
- **Metadata Filtering** — filter by library, category, tags, etc.
- **Top-K** — configurable number of returned chunks.

Every result carries a similarity score, source file path, source URL, and chunk ID.

### 8. RAG Pipeline

`pipeline/rag_chain.py` implements a **LangGraph** stateful workflow:

```
[User Query]
    │
    ▼
[Retrieve Chunks]  ←─ vector store
    │
    ▼
[Build Context]
    │
    ▼
[LLM Generate]  ←─ prompt template
    │
    ▼
[Extract Citations]
    │
    ▼
[Return Answer + Sources]
```

If no relevant context is found, the assistant responds:
> *"I couldn't find this information in the documentation."*

---

## Running the Streamlit App

```bash
streamlit run ui/app.py
```

The interface provides:

- **Chat panel** — conversational QA with the documentation.
- **Source viewer** — expandable source document cards.
- **Chunk viewer** — raw retrieved chunks with similarity scores.
- **Metadata panel** — document metadata for each retrieved chunk.
- **Response time** — latency display per query.
- **Settings sidebar** — switch retrieval method, adjust Top-K, select LLM model.

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test module
pytest tests/test_crawler.py -v
pytest tests/test_rag_pipeline.py -v
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `FAISS not found` | Run `pip install faiss-cpu` |
| `Playwright browser missing` | Run `playwright install chromium` |
| `ChromaDB migration error` | Delete `vectordb_storage/` and re-ingest |
| `LLM API key invalid` | Verify your `.env` values |
| `No documents found` | Check `knowledge_base/` and re-run ingestion |
| `Embedding mismatch` | Ensure `EMBEDDING_MODEL` is consistent between ingestion and query |
| `Crawl returns 0 pages` | Try a different `CRAWLER_TYPE` in `.env` |

Check `logs/app.log` for detailed error traces.

---

## Future Improvements

- [ ] **Multi-modal RAG** — embed images and diagrams from documentation.
- [ ] **Hybrid search** — combine BM25 sparse retrieval with dense embeddings.
- [ ] **Re-ranking** — add a cross-encoder re-ranker (e.g., `ms-marco-MiniLM`) post-retrieval.
- [ ] **Incremental ingestion** — detect and re-ingest only changed pages.
- [ ] **Document versioning** — track documentation version history.
- [ ] **Authentication** — optional password-protected Streamlit deployment.
- [ ] **API endpoint** — FastAPI wrapper for integration with external systems.
- [ ] **Multi-language support** — multilingual embedding models.
