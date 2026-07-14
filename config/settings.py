"""
config/settings.py
------------------
Centralised application configuration loaded from environment variables.

Purpose       : Parse and validate all settings using pydantic-settings so every
                module gets strongly-typed, default-safe values from one source.
Dependencies  : pydantic-settings, python-dotenv
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

# pyrefly: ignore [missing-import]
from pydantic import Field, field_validator
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Helper – resolve absolute paths relative to the project root
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application-wide settings.  Values are read from the environment / .env file.
    All paths are resolved to absolute paths at validation time.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------
    openai_api_key: str = Field(default="", description="OpenAI API key.")
    groq_api_key: str = Field(default="", description="Groq API key.")
    anthropic_api_key: str = Field(default="", description="Anthropic API key.")

    llm_provider: Literal["openai", "groq", "anthropic"] = Field(
        default="groq",
        description="Which LLM provider to use.",
    )
    llm_model: str = Field(
        default="llama3-8b-8192",
        description="Model identifier for the selected provider.",
    )
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature.",
    )

    # ------------------------------------------------------------------
    # Crawler — core
    # ------------------------------------------------------------------
    firecrawl_api_key: str = Field(default="", description="Firecrawl API key.")
    crawler_type: Literal["firecrawl", "crawl4ai", "trafilatura", "beautifulsoup"] = Field(
        default="trafilatura",
        description="Preferred crawler backend (used as first choice by the router).",
    )
    max_depth: int = Field(default=3, ge=1, description="Maximum crawl depth.")
    concurrent_requests: int = Field(
        default=5, ge=1, le=20, description="Parallel HTTP requests during crawl."
    )

    # ------------------------------------------------------------------
    # Crawler — politeness
    # ------------------------------------------------------------------
    crawl_delay_seconds: float = Field(
        default=0.5,
        ge=0.0,
        description="Minimum seconds between consecutive requests to the same domain.",
    )
    crawl_force_robots: bool = Field(
        default=False,
        description=(
            "If True, URLs disallowed by robots.txt are skipped entirely. "
            "If False, a warning is logged but crawling proceeds (useful for "
            "documentation sites that block all bots indiscriminately)."
        ),
    )

    # ------------------------------------------------------------------
    # Crawler — URL filtering
    # ------------------------------------------------------------------
    crawl_allow_pdf: bool = Field(
        default=False,
        description="If True, PDF URLs are crawled instead of filtered out.",
    )
    crawl_allowed_domains: list[str] = Field(
        default_factory=list,
        description=(
            "Explicit list of allowed domain names (e.g. ['docs.python.org']). "
            "Empty = same-domain-only restriction."
        ),
    )
    crawl_allowed_prefixes: list[str] = Field(
        default_factory=list,
        description=(
            "Explicit list of allowed URL prefixes. "
            "Takes precedence over crawl_allowed_domains."
        ),
    )

    # ------------------------------------------------------------------
    # Crawler — content validation
    # ------------------------------------------------------------------
    crawl_min_content_chars: int = Field(
        default=150,
        ge=10,
        description="Minimum character count for a page to be ingested.",
    )
    crawl_min_content_words: int = Field(
        default=30,
        ge=5,
        description="Minimum word count for a page to be ingested.",
    )

    # ------------------------------------------------------------------
    # Crawler — backend behaviour
    # ------------------------------------------------------------------
    crawl_backend_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Per-request timeout in seconds for all crawler backends.",
    )
    crawl_max_retries_per_backend: int = Field(
        default=2,
        ge=1,
        le=5,
        description=(
            "Maximum retry attempts per backend before escalating to the next backend. "
            "Reduced from the original 3 to limit Firecrawl API costs."
        ),
    )

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="HuggingFace model for generating embeddings.",
    )
    embedding_batch_size: int = Field(
        default=64, ge=1, description="Batch size for embedding generation."
    )

    # ------------------------------------------------------------------
    # Vector Database
    # ------------------------------------------------------------------
    vector_db_type: Literal["chroma", "faiss"] = Field(
        default="chroma",
        description="Vector database backend.",
    )
    vector_db_dir: Path = Field(
        default=PROJECT_ROOT / "vectordb_storage",
        description="Directory where vector index is persisted.",
    )

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------
    chunk_size: int = Field(default=800, ge=100, description="Target chunk size (tokens).")
    chunk_overlap: int = Field(default=150, ge=0, description="Overlap between chunks.")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    retrieval_top_k: int = Field(
        default=8, ge=1, le=30, description="Number of chunks to retrieve per query (final, after rerank)."
    )
    retrieval_method: Literal["similarity", "mmr"] = Field(
        default="mmr",
        description="Retrieval strategy: similarity search or MMR.",
    )
    retrieval_min_score: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum similarity score for a chunk to be included in the LLM context. "
            "Chunks below this score are discarded before generation. "
            "Lower values = more permissive (good for broad/comparison queries). "
            "Higher values = stricter relevance (good for narrow factual queries). "
            "Default 0.1 replaced the previous hardcoded 0.3 which was too aggressive."
        ),
    )
    mmr_fetch_k: int = Field(
        default=30,
        ge=1,
        description="Candidate pool size for MMR retrieval.",
    )
    mmr_lambda_mult: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="MMR lambda (diversity vs. relevance balance).",
    )

    # ------------------------------------------------------------------
    # Hybrid Retrieval
    # ------------------------------------------------------------------
    hybrid_search_enabled: bool = Field(
        default=True,
        description="Use hybrid BM25 + semantic retrieval instead of semantic-only.",
    )
    hybrid_candidate_k: int = Field(
        default=30,
        ge=5,
        description="Number of candidates fetched from each retriever (BM25 + semantic) before fusion.",
    )
    bm25_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="BM25 contribution weight in RRF fusion (0 = semantic only, 1 = BM25 only).",
    )
    reranker_enabled: bool = Field(
        default=True,
        description="Apply cross-encoder reranking after RRF fusion.",
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="HuggingFace cross-encoder model for reranking.",
    )
    rerank_top_n: int = Field(
        default=12,
        ge=1,
        description="Number of candidates to feed to the cross-encoder reranker.",
    )
    context_expansion_enabled: bool = Field(
        default=True,
        description="Include adjacent chunks (chunk_index ± 1) for context continuity.",
    )

    # ------------------------------------------------------------------
    # Multi-Hop Retrieval
    # ------------------------------------------------------------------
    multi_hop_enabled: bool = Field(
        default=True,
        description="Run a second retrieval hop when the initial context is thin.",
    )
    multi_hop_max_hops: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of additional retrieval hops.",
    )
    multi_hop_min_words: int = Field(
        default=200,
        ge=50,
        description="Trigger multi-hop when total retrieved context has fewer words than this.",
    )

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    knowledge_base_dir: Path = Field(
        default=PROJECT_ROOT / "knowledge_base",
        description="Root directory for crawled Markdown documents.",
    )
    log_dir: Path = Field(
        default=PROJECT_ROOT / "logs",
        description="Directory for application log files.",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging verbosity level.",
    )

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("vector_db_dir", "knowledge_base_dir", "log_dir", mode="before")
    @classmethod
    def _resolve_path(cls, v: str | Path) -> Path:
        """Resolve paths relative to project root and ensure they are absolute."""
        path = Path(v)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def active_api_key(self) -> str:
        """Return the API key for the currently selected LLM provider."""
        mapping = {
            "openai": self.openai_api_key,
            "groq": self.groq_api_key,
            "anthropic": self.anthropic_api_key,
        }
        return mapping[self.llm_provider]

    def vector_db_path(self) -> Path:
        """Return the full path to the vector database storage directory."""
        return self.vector_db_dir / self.vector_db_type


# ---------------------------------------------------------------------------
# Module-level singleton – import this everywhere
# ---------------------------------------------------------------------------
settings = Settings()
