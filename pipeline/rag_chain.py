"""
pipeline/rag_chain.py
---------------------
Multi-document RAG pipeline implemented as a LangGraph StateGraph.

Architecture
------------
  condense_question
        ↓
  hybrid_retrieve       (BM25 + semantic → RRF → cross-encoder rerank → context expand)
        ↓
  multi_hop             (checks context sufficiency; generates sub-query & re-retrieves
                         up to settings.multi_hop_max_hops times if context is thin)
        ↓
  generate              (multi-doc synthesis prompt → grounded, cited answer)

LLM Providers : Groq (default), OpenAI, Anthropic – selected via .env.

Dependencies  : langchain-core, langchain-community, langgraph,
                retrieval.hybrid_retriever, retrieval.searcher,
                prompts.templates, config.settings, config.logging_config
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph

from config.logging_config import get_logger
from config.settings import settings
from prompts.templates import (
    CONDENSE_PROMPT,
    MULTI_HOP_PROMPT,
    RAG_CHAT_PROMPT,
    format_context,
)
from retrieval.searcher import SearchResult, get_searcher

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RAGResponse:
    """Structured response from the RAG pipeline."""

    answer: str
    sources: list[SearchResult] = field(default_factory=list)
    standalone_question: str = ""
    context: str = ""
    elapsed_seconds: float = 0.0
    model: str = ""
    retrieved_count: int = 0
    hops_used: int = 0


# ---------------------------------------------------------------------------
# LangGraph state schema
# ---------------------------------------------------------------------------

class RAGState(TypedDict, total=False):
    """Mutable state dict passed between LangGraph nodes."""

    question: str
    chat_history: list[BaseMessage]
    standalone_question: str
    retrieved_docs: list[SearchResult]
    context: str
    answer: str
    library_filter: Optional[str]
    hop_count: int          # number of multi-hop retrieval iterations completed


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _build_llm():
    """
    Instantiate the LLM based on settings.llm_provider.

    Returns:
        LangChain chat model instance.

    Raises:
        ValueError: If the configured provider is unknown.
        ImportError: If the required provider package is not installed.
    """
    provider = settings.llm_provider
    model = settings.llm_model
    temperature = settings.llm_temperature
    api_key = settings.active_api_key()

    logger.info("Building LLM | provider=%s | model=%s", provider, model)

    if provider == "groq":
        # pyrefly: ignore [missing-import]
        from langchain_groq import ChatGroq  # noqa: PLC0415
        return ChatGroq(model=model, temperature=temperature, api_key=api_key)

    if provider == "openai":
        from langchain_openai import ChatOpenAI  # noqa: PLC0415
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic  # noqa: PLC0415
        return ChatAnthropic(model=model, temperature=temperature, api_key=api_key)

    raise ValueError(f"Unknown LLM provider: {provider!r}")


# ---------------------------------------------------------------------------
# RAG Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """
    Full multi-document RAG pipeline implemented as a LangGraph StateGraph.

    Retrieval uses hybrid BM25 + semantic search with RRF fusion and
    cross-encoder reranking.  Multi-hop retrieval runs automatically when
    the initial context is insufficient.

    Usage::

        pipeline = RAGPipeline()
        response = pipeline.ask("What is LangChain?")
        print(response.answer)

    Args:
        library_filter : Optional library name to restrict retrieval.
        top_k          : Number of final chunks to retrieve (default from settings).
    """

    def __init__(
        self,
        library_filter: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> None:
        self.library_filter = library_filter
        self.top_k = top_k or settings.retrieval_top_k
        self._llm = _build_llm()
        self._searcher = get_searcher()
        self._graph = self._build_graph()
        logger.info(
            "RAGPipeline ready | provider=%s | model=%s | top_k=%d | hybrid=%s | multi_hop=%s",
            settings.llm_provider,
            settings.llm_model,
            self.top_k,
            settings.hybrid_search_enabled,
            settings.multi_hop_enabled,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(
        self,
        question: str,
        chat_history: Optional[list[BaseMessage]] = None,
        library_filter: Optional[str] = None,
    ) -> RAGResponse:
        """
        Run the full RAG pipeline for a single question.

        Args:
            question      : User's natural language question.
            chat_history  : Previous messages for multi-turn context.
            library_filter: Restrict retrieval to a specific library.

        Returns:
            :class:`RAGResponse` with answer, sources, and metadata.
        """
        t0 = time.monotonic()
        initial_state: RAGState = {
            "question": question,
            "chat_history": chat_history or [],
            "standalone_question": "",
            "retrieved_docs": [],
            "context": "",
            "answer": "",
            "library_filter": library_filter or self.library_filter,
            "hop_count": 0,
        }

        try:
            final_state: RAGState = self._graph.invoke(
                initial_state,
                config=RunnableConfig(recursion_limit=15),
            )
        except Exception as exc:
            logger.error("RAG pipeline error: %s", exc, exc_info=True)
            return RAGResponse(
                answer="An error occurred while generating the response. Please try again later.",
                elapsed_seconds=time.monotonic() - t0,
                model=settings.llm_model,
            )

        return RAGResponse(
            answer=final_state.get("answer", "I couldn't generate a response."),
            sources=final_state.get("retrieved_docs", []),
            standalone_question=final_state.get("standalone_question", question),
            context=final_state.get("context", ""),
            elapsed_seconds=time.monotonic() - t0,
            model=settings.llm_model,
            retrieved_count=len(final_state.get("retrieved_docs", [])),
            hops_used=final_state.get("hop_count", 0),
        )

    def stream(
        self,
        question: str,
        chat_history: Optional[list[BaseMessage]] = None,
        library_filter: Optional[str] = None,
    ):
        """
        Stream the RAG answer token-by-token.

        Yields:
            str: Individual text tokens.
        """
        standalone = self._condense(question, chat_history or [])
        docs = self._retrieve(standalone, library_filter or self.library_filter)
        # Apply multi-hop if context is thin
        if settings.multi_hop_enabled:
            docs = self._do_multi_hop(standalone, docs, library_filter or self.library_filter)
            
        min_score = settings.retrieval_min_score
        valid_docs = [d for d in docs if getattr(d, 'score', 0) >= min_score]
        if not docs or not valid_docs:
            yield "⚠️ This information is not available in the ingested documentation."
            return
        
        db_count = self._searcher.count()
        context = format_context(docs, db_count=db_count)

        chain = RAG_CHAT_PROMPT | self._llm | StrOutputParser()
        yield from chain.stream(
            {
                "context": context,
                "question": standalone,
                "chat_history": chat_history or [],
            }
        )

    # ------------------------------------------------------------------
    # LangGraph node functions
    # ------------------------------------------------------------------

    def _node_condense(self, state: RAGState) -> RAGState:
        """Node 1: Condense chat history into a standalone question."""
        question = state["question"]
        history = state.get("chat_history", [])

        if not history:
            state["standalone_question"] = question
            return state

        logger.debug("Condensing question with %d history messages.", len(history))
        chain = CONDENSE_PROMPT | self._llm | StrOutputParser()
        standalone = chain.invoke(
            {"chat_history": _format_history(history), "question": question}
        )
        state["standalone_question"] = standalone.strip()
        return state

    def _node_retrieve(self, state: RAGState) -> RAGState:
        """Node 2: Hybrid retrieval (BM25 + semantic → RRF → rerank → expand)."""
        standalone = state.get("standalone_question") or state["question"]
        lib_filter = state.get("library_filter")

        docs = self._retrieve(standalone, lib_filter)
        state["retrieved_docs"] = docs
        
        db_count = self._searcher.count()
        state["context"] = format_context(docs, db_count=db_count)

        logger.info("Retrieved %d chunk(s) for: %r", len(docs), standalone[:80])
        return state

    def _node_multi_hop(self, state: RAGState) -> RAGState:
        """
        Node 3: Multi-hop retrieval.

        If the current context is thin (< settings.multi_hop_min_words words),
        the LLM generates a focused sub-query and we retrieve again, merging
        new unique documents with the existing set.

        Repeats up to settings.multi_hop_max_hops times.
        """
        if not settings.multi_hop_enabled:
            return state

        hop_count = state.get("hop_count", 0)
        results = state.get("retrieved_docs", [])
        question = state.get("standalone_question") or state["question"]
        lib_filter = state.get("library_filter")

        while hop_count < settings.multi_hop_max_hops:
            total_words = sum(len(r.text.split()) for r in results)
            if total_words >= settings.multi_hop_min_words:
                logger.info(
                    "Multi-hop: context sufficient (%d words) – stopping at hop %d.",
                    total_words, hop_count,
                )
                break

            logger.info(
                "Multi-hop: thin context (%d words) – generating sub-query (hop %d/%d).",
                total_words, hop_count + 1, settings.multi_hop_max_hops,
            )

            # Generate a focused sub-query
            context_summary = format_context(results)[:600]
            try:
                chain = MULTI_HOP_PROMPT | self._llm | StrOutputParser()
                sub_query = chain.invoke(
                    {"question": question, "context_summary": context_summary}
                ).strip()
            except Exception as exc:
                logger.warning("Sub-query generation failed: %s", exc)
                break

            if not sub_query:
                break

            logger.info("Sub-query: %r", sub_query[:100])

            # Retrieve with sub-query and merge unique results
            new_docs = self._retrieve(sub_query, lib_filter)
            existing_ids = {r.chunk_id for r in results}
            for doc in new_docs:
                if doc.chunk_id not in existing_ids:
                    existing_ids.add(doc.chunk_id)
                    results.append(doc)

            hop_count += 1

        state["retrieved_docs"] = results
        db_count = self._searcher.count()
        state["context"] = format_context(results, db_count=db_count)
        state["hop_count"] = hop_count
        return state

    def _node_generate(self, state: RAGState) -> RAGState:
        """Node 4: Generate a synthesised, grounded, cited answer."""
        docs = state.get("retrieved_docs", [])
        min_score = settings.retrieval_min_score
        valid_docs = [d for d in docs if getattr(d, 'score', 0) >= min_score]
        if not docs or not valid_docs:
            state["answer"] = "⚠️ This information is not available in the ingested documentation."
            return state

        context = state.get("context", "")
        question = state.get("standalone_question") or state["question"]
        history = state.get("chat_history", [])

        chain = RAG_CHAT_PROMPT | self._llm | StrOutputParser()
        answer = chain.invoke(
            {
                "context": context,
                "question": question,
                "chat_history": history,
            }
        )
        state["answer"] = answer
        logger.info(
            "Answer generated (%d chars) | hops=%d | sources=%d.",
            len(answer),
            state.get("hop_count", 0),
            len(state.get("retrieved_docs", [])),
        )
        return state

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self) -> StateGraph:
        """Assemble the LangGraph StateGraph."""
        graph = StateGraph(RAGState)

        graph.add_node("condense_question", self._node_condense)
        graph.add_node("retrieve", self._node_retrieve)
        graph.add_node("multi_hop", self._node_multi_hop)
        graph.add_node("generate", self._node_generate)

        graph.set_entry_point("condense_question")
        graph.add_edge("condense_question", "retrieve")
        graph.add_edge("retrieve", "multi_hop")
        graph.add_edge("multi_hop", "generate")
        graph.add_edge("generate", END)

        return graph.compile()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _condense(self, question: str, history: list[BaseMessage]) -> str:
        """Condense follow-up question using chat history."""
        if not history:
            return question
        chain = CONDENSE_PROMPT | self._llm | StrOutputParser()
        return chain.invoke(
            {"chat_history": _format_history(history), "question": question}
        ).strip()

    def _retrieve(
        self,
        query: str,
        library_filter: Optional[str],
    ) -> list[SearchResult]:
        """Run hybrid or fallback retrieval for *query*."""
        if settings.hybrid_search_enabled:
            from retrieval.hybrid_retriever import get_hybrid_retriever  # noqa: PLC0415
            retriever = get_hybrid_retriever()
            return retriever.retrieve(
                query=query,
                k=self.top_k,
                library_filter=library_filter,
                candidate_k=settings.hybrid_candidate_k,
                rerank=settings.reranker_enabled,
                expand_context=settings.context_expansion_enabled,
            )

        # Fallback: original single-strategy searcher
        if library_filter:
            return self._searcher.search_by_library(
                query=query, library=library_filter, k=self.top_k
            )
        return self._searcher.search(query=query, k=self.top_k)

    def _do_multi_hop(
        self,
        question: str,
        docs: list[SearchResult],
        library_filter: Optional[str],
    ) -> list[SearchResult]:
        """
        Inline multi-hop helper used by the ``stream()`` path
        (which bypasses the LangGraph graph).
        """
        hop = 0
        while hop < settings.multi_hop_max_hops:
            total_words = sum(len(r.text.split()) for r in docs)
            if total_words >= settings.multi_hop_min_words:
                break
            db_count = self._searcher.count()
            context_summary = format_context(docs, db_count=db_count)[:600]
            try:
                chain = MULTI_HOP_PROMPT | self._llm | StrOutputParser()
                sub_query = chain.invoke(
                    {"question": question, "context_summary": context_summary}
                ).strip()
            except Exception:
                break
            if not sub_query:
                break
            new_docs = self._retrieve(sub_query, library_filter)
            existing_ids = {r.chunk_id for r in docs}
            for doc in new_docs:
                if doc.chunk_id not in existing_ids:
                    existing_ids.add(doc.chunk_id)
                    docs.append(doc)
            hop += 1
        return docs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_history(messages: list[BaseMessage]) -> str:
    """Convert a list of LangChain messages into a readable string."""
    lines: list[str] = []
    for msg in messages:
        role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Convenience function for simple one-shot usage
# ---------------------------------------------------------------------------

def ask(
    question: str,
    chat_history: Optional[list[BaseMessage]] = None,
    library_filter: Optional[str] = None,
) -> RAGResponse:
    """
    Module-level convenience function to run the RAG pipeline.

    Args:
        question      : User's question.
        chat_history  : Optional conversation history.
        library_filter: Optional library filter.

    Returns:
        :class:`RAGResponse`.
    """
    pipeline = RAGPipeline(library_filter=library_filter)
    return pipeline.ask(question, chat_history=chat_history)
