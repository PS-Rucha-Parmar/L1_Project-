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
8. [Changelog](#changelog)
9. [Troubleshooting](#troubleshooting)
10. [Future Improvements](#future-improvements)

---

## Architecture Overview

```
Documentation URL(s)
       │
       ▼
┌──────────────┐
│   Crawler    │  BackendRouter → Firecrawl / Crawl4AI / Trafilatura / BeautifulSoup
│              │  URLFilter → RobotsChecker → CrawlLimiter → ContentValidator
└──────┬───────┘
       │ clean Markdown + CrawlEvent log
       ▼
┌──────────────┐
│  Preprocessor│  Clean → Chunk → Generate metadata.json
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
│   ├── __init__.py          # Public API: crawl(), DocumentationSpider
│   ├── spider.py            # Slim orchestrator (~200 lines)
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── base.py          # CrawlResult, ErrorType, _BaseCrawler
│   │   ├── firecrawl.py     # Cloud API backend (JS-heavy pages)
│   │   ├── crawl4ai.py      # Async Playwright backend
│   │   ├── trafilatura.py   # Fast HTTP extraction backend
│   │   └── beautifulsoup.py # Reliable HTML-parsing fallback
│   ├── router.py            # Intelligent backend selection + smart retry
│   ├── filters.py           # URL canonicalization, filtering, domain restriction
│   ├── politeness.py        # robots.txt enforcement + per-domain rate limiting
│   ├── validator.py         # Content quality validation (error/CAPTCHA/login detection)
│   ├── extractor.py         # Link extraction (HTML + Markdown) + MarkdownBuilder
│   ├── queue.py             # BFS/DFS/priority queue with deduplication
│   └── report.py            # CrawlEvent per-URL + IngestionReport + JSON output
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
│   └── searcher.py          # Similarity search, MMR (with real scores), Top-K, metadata filters
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
│   │   └── crawl_report.json  # Per-URL crawl event log (NEW)
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
git clone https://github.com/PS-Rucha-Parmar/L1_Project-.git
cd L1_Project-

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (required by Crawl4AI)
playwright install chromium

# 5. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and preferred settings
```

### Running (Short Form — no activation needed)

```powershell
# From the project root (DocAi/DocAi/)
..\.venv\Scripts\streamlit run ui\app.py
```

---

## Configuration

All configuration is managed through the `.env` file. See `.env.example` for the full list.

### LLM

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | LLM backend: `groq`, `openai`, `anthropic` |
| `LLM_MODEL` | `llama3-8b-8192` | Model identifier |
| `LLM_TEMPERATURE` | `0.0` | Sampling temperature |

### Crawler — Core

| Variable | Default | Description |
|---|---|---|
| `CRAWLER_TYPE` | `trafilatura` | Preferred backend (router still escalates automatically) |
| `MAX_DEPTH` | `3` | Maximum recursive link depth |
| `CONCURRENT_REQUESTS` | `5` | Parallel requests (reserved for future async mode) |

### Crawler — Politeness (NEW)

| Variable | Default | Description |
|---|---|---|
| `CRAWL_DELAY_SECONDS` | `0.5` | Min seconds between requests to same domain |
| `CRAWL_FORCE_ROBOTS` | `false` | Enforce robots.txt disallow rules strictly |

### Crawler — URL Filtering (NEW)

| Variable | Default | Description |
|---|---|---|
| `CRAWL_ALLOW_PDF` | `false` | Include PDF files in crawl |
| `CRAWL_ALLOWED_DOMAINS` | *(empty)* | Comma-separated domain allowlist |
| `CRAWL_ALLOWED_PREFIXES` | *(empty)* | Comma-separated URL prefix allowlist |

### Crawler — Content Validation (NEW)

| Variable | Default | Description |
|---|---|---|
| `CRAWL_MIN_CONTENT_CHARS` | `150` | Reject pages shorter than this |
| `CRAWL_MIN_CONTENT_WORDS` | `30` | Reject pages with fewer words |

### Crawler — Backend Behaviour (NEW)

| Variable | Default | Description |
|---|---|---|
| `CRAWL_BACKEND_TIMEOUT_SECONDS` | `30` | Per-request timeout for all backends |
| `CRAWL_MAX_RETRIES_PER_BACKEND` | `2` | Max retries before escalating to next backend |

### Embeddings & Retrieval

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | SentenceTransformer model |
| `VECTOR_DB_TYPE` | `chroma` | `chroma` or `faiss` |
| `RETRIEVAL_TOP_K` | `8` | Chunks returned per query |
| `RETRIEVAL_METHOD` | `mmr` | `similarity` or `mmr` |
| `RETRIEVAL_MIN_SCORE` | `0.1` | Min score for chunk to enter LLM context (NEW) |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Pipeline Walkthrough

### 1. Crawling

The crawler module (`crawler/`) is now a fully modular pipeline:

**Backend Router** (`crawler/router.py`) — intelligently selects the cheapest capable backend based on URL signals, instead of blindly trying all backends:

| URL Signal | Primary | Fallback |
|---|---|---|
| Static docs (`.readthedocs.io`, `/docs/`) | Trafilatura | BeautifulSoup |
| GitHub / wiki pages | Trafilatura | BeautifulSoup |
| JS-heavy / SPA | Crawl4AI | Firecrawl |
| Unknown | Trafilatura → BeautifulSoup | Crawl4AI |

**Smart Retry Logic** — each error type gets a different action:

| Error Type | Action |
|---|---|
| `EMPTY` | Escalate to next backend immediately |
| `TIMEOUT` | Retry once, then escalate |
| `RATE_LIMIT` | Sleep exponentially, retry same backend |
| `AUTH` | Skip entirely — never retry |
| `NETWORK` | Retry once, then escalate |

**URL Filter** (`crawler/filters.py`) — strips tracking parameters and rejects non-content pages:
- Strips: `utm_source`, `utm_medium`, `fbclid`, `gclid`, and 15+ tracking params
- Rejects: `/login`, `/signup`, `/privacy`, `/terms`, `/cookies`, `/share`, `/profile`, etc.
- Enforces same-domain restriction (configurable to multi-domain)

**Content Validator** (`crawler/validator.py`) — rejects pages before ingestion:
- Error pages (404/403 returning HTTP 200)
- CAPTCHA / bot-detection pages
- Cookie consent walls
- Login / authentication walls
- Navigation-only pages (>75% link text)

**Crawl Report** — every crawl writes `knowledge_base/<library>/crawl_report.json` with a structured per-URL event log.

### 2. Cleaning & Markdown Generation

`preprocessing/cleaner.py` strips navigation bars, sidebars, footers, advertisements, JavaScript, CSS, cookie banners, and duplicate paragraphs.

`crawler/extractor.py` — `MarkdownBuilder` generates clean Markdown with only content-driven sections (no more 14 empty placeholder headings), plus YAML frontmatter:

```markdown
---
title: "Page Title"
url: "https://..."
library: "langchain"
backend: "trafilatura"
word_count: 342
crawled_at: "2026-07-14T06:00:00Z"
---

## Content

(extracted text)

## References

- Source: [url](url)
```

### 3. Metadata

`preprocessing/metadata.py` generates a `_metadata.json` beside every Markdown file containing: `id`, `title`, `library`, `topic`, `url`, `category`, `tags`, `word_count`, `reading_time`, `backend`, `created`, `updated`, `embedding_status`.

### 4. Chunking

`preprocessing/chunker.py` applies **semantic chunking first**, falling back to `RecursiveCharacterTextSplitter` (chunk size 800, overlap 150). Code blocks, tables, lists, and examples are never split mid-structure.

### 5. Embeddings

`embeddings/embedder.py` uses `BAAI/bge-small-en-v1.5` via SentenceTransformers. Documents are processed in configurable batches.

### 6. Vector Database

`vectordb/vector_store.py` wraps both **ChromaDB** (default) and **FAISS** (optional) behind a unified interface. Indexes are persisted to `vectordb_storage/` on every write.

### 7. Retrieval

`retrieval/searcher.py` supports:
- **Similarity Search** — cosine distance ranking with real scores.
- **MMR (Maximal Marginal Relevance)** — balances relevance and diversity. Now assigns **real similarity scores** via a parallel lookup (previously hardcoded `1.0` which blocked answer generation).
- **Metadata Filtering** — filter by library, category, tags, etc.
- **Configurable Min Score** — `RETRIEVAL_MIN_SCORE=0.1` controls the threshold for including chunks in the LLM context.

### 8. RAG Pipeline

`pipeline/rag_chain.py` implements a **LangGraph** stateful workflow:

```
[User Query]
    │
    ▼
[Condense Question]  ←─ chat history
    │
    ▼
[Hybrid Retrieve]    ←─ BM25 + semantic → RRF → cross-encoder rerank
    │
    ▼
[Multi-Hop]         ←─ re-retrieves if context is thin
    │
    ▼
[Score Filter]      ←─ settings.retrieval_min_score (default 0.1)
    │
    ▼
[LLM Generate]      ←─ prompt template
    │
    ▼
[Return Answer + Sources]
```

---

## Running the Streamlit App

```bash
# Method 1: Activate virtual env first
..\.venv\Scripts\Activate.ps1
streamlit run ui\app.py

# Method 2: Direct (no activation needed)
..\.venv\Scripts\streamlit run ui\app.py
```

The interface provides:

- **Chat panel** — conversational QA with the documentation.
- **Source viewer** — expandable source document cards with similarity scores.
- **Chunk viewer** — raw retrieved chunks with metadata.
- **Response time** — latency display per query.
- **Settings sidebar** — switch retrieval method, adjust Top-K, select LLM model.
- **Ingestion wizard** — crawl new docs directly from the UI.

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

## Changelog

### v2.0.0 — Crawler Redesign (2026-07-14)

#### 🆕 New Modules
- `crawler/backends/` — each backend isolated in its own module with lazy instantiation
- `crawler/backends/base.py` — `CrawlResult`, `ErrorType` enum, `_BaseCrawler` abstract class
- `crawler/router.py` — intelligent backend selection (URL classification + smart per-error retry)
- `crawler/filters.py` — URL canonicalization (strips UTM/tracking params) + configurable URL filter
- `crawler/politeness.py` — robots.txt enforcement + per-domain `CrawlLimiter`
- `crawler/validator.py` — content quality validation (rejects error pages, CAPTCHA, login walls)
- `crawler/extractor.py` — link extraction from both HTML **and** Markdown (fixes JS-site recursion)
- `crawler/queue.py` — BFS/DFS/priority queue with retry sub-queue
- `crawler/report.py` — structured `CrawlEvent` per URL + `crawl_report.json` output

#### 🔧 Bugs Fixed
- **robots.txt bypass** — was fetched but never enforced; now configurable via `CRAWL_FORCE_ROBOTS`
- **Blind backend retry** — 4 backends × 3 retries = 12 calls per URL; now signal-based routing
- **UTM param duplicates** — `?utm_source=email` and `?utm_source=twitter` stored as 2 docs; fixed
- **Link extraction on JS sites** — broke when Firecrawl/Crawl4AI returned Markdown (no HTML); fixed
- **14 empty section headings** — generated ~14 useless vector DB chunks per document; removed
- **No content validation** — error pages and login walls ingested; now rejected before storage
- **BeautifulSoup duplicate text** — `soup.descendants` visited nodes multiple times; fixed
- **MMR score hardcoded 1.0** — all MMR results got `score=1.0` causing the score filter to fail; fixed with real parallel similarity lookup
- **Score threshold too strict** — hardcoded `0.3` rejected valid broad/comparison queries; now `RETRIEVAL_MIN_SCORE=0.1`

#### ⚙️ New Settings
`CRAWL_DELAY_SECONDS`, `CRAWL_FORCE_ROBOTS`, `CRAWL_ALLOW_PDF`, `CRAWL_ALLOWED_DOMAINS`, `CRAWL_ALLOWED_PREFIXES`, `CRAWL_MIN_CONTENT_CHARS`, `CRAWL_MIN_CONTENT_WORDS`, `CRAWL_BACKEND_TIMEOUT_SECONDS`, `CRAWL_MAX_RETRIES_PER_BACKEND`, `RETRIEVAL_MIN_SCORE`

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
| `Crawl returns 0 pages` | Try a different `CRAWLER_TYPE` in `.env`; check `crawl_report.json` for details |
| `⚠️ Not available` despite docs existing | Lower `RETRIEVAL_MIN_SCORE` in `.env` (try `0.05`) |
| `Crawl blocked by robots.txt` | Set `CRAWL_FORCE_ROBOTS=false` in `.env` |

Check `logs/app.log` and `knowledge_base/<library>/crawl_report.json` for detailed error traces.

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
- [ ] **Async crawling** — use the existing `concurrent_requests` setting for parallel fetching.
- [ ] **Query decomposition** — detect comparison queries and retrieve from each library independently.
