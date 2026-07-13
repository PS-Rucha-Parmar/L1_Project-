"""
ui/app.py
---------
DocAI Streamlit Application.

Purpose       : Provide a modern, dark-themed chat interface for the RAG
                pipeline with:
                  - Streaming LLM responses
                  - Expandable source viewer (retrieved chunks + scores)
                  - Sidebar ingestion wizard (crawl new docs, embed, index)
                  - Library selector / filter
                  - Metadata badges (response time, model, chunk count)
                  - Dark glassmorphism theme

Run with::

    streamlit run ui/app.py

Dependencies  : streamlit, pipeline.rag_chain, retrieval.searcher,
                crawler.spider, preprocessing, embeddings, vectordb,
                utils.helpers, config.settings
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on the path when running from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from config.logging_config import get_logger, setup_logging
from config.settings import settings
from utils.helpers import count_documents, format_elapsed, truncate_text

setup_logging(log_level=settings.log_level)
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Page config – must be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="DocAI – Documentation Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS – dark glassmorphism theme
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-base:#080b12; --bg-surface:#0f1320; --bg-elevated:#151a2b; --bg-input:#1c2337;
  --border:rgba(56,189,248,0.13); --border-bright:rgba(56,189,248,0.4);
  --accent:#38bdf8; --accent2:#818cf8; --accent3:#34d399;
  --glow:rgba(56,189,248,0.22);
  --text:#f1f5f9; --text-muted:#64748b; --text-code:#7dd3fc;
  --radius:14px; --radius-lg:20px;
}
html,body,[class*="css"],.stApp,[data-testid="stBottom"],[data-testid="stBottom"] > div,[data-testid="stHeader"]{font-family:'Inter',sans-serif!important;background-color:var(--bg-base)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;} .stDeployButton{display:none;}
.block-container{padding:1.5rem 2rem 6rem!important;max-width:1400px;}
[data-testid="stSidebar"]{background:var(--bg-surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] .block-container{padding:1.5rem 1rem!important;}
.docai-logo{display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0 1.4rem;border-bottom:1px solid var(--border);margin-bottom:1.4rem;}
.docai-logo h1{font-size:1.5rem;font-weight:800;margin:0;background:linear-gradient(130deg,#38bdf8 0%,#818cf8 50%,#34d399 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.docai-logo span{font-size:1.9rem;}
.sidebar-section{font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-muted);margin:1.4rem 0 0.5rem;}
.source-card{background:linear-gradient(135deg,rgba(56,189,248,0.04),rgba(129,140,248,0.04));border:1px solid var(--border);border-radius:var(--radius);padding:0.7rem 1rem;margin-bottom:0.45rem;transition:border-color .2s,box-shadow .2s;}
.source-card:hover{border-color:var(--border-bright);box-shadow:0 0 18px var(--glow);}
.source-score{font-size:0.74rem;font-weight:700;color:var(--accent);font-family:'JetBrains Mono',monospace;}
.stChatMessage{background:var(--bg-elevated)!important;border:1px solid var(--border)!important;border-radius:var(--radius-lg)!important;margin-bottom:1rem!important;padding:1rem 1.3rem!important;animation:fadeUp .3s ease;}
.stChatMessage p, .stChatMessage li, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, .stMarkdown p, .stMarkdown li { color: var(--text) !important; }
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){border-left:3px solid var(--accent3)!important;background:linear-gradient(135deg,rgba(52,211,153,.07) 0%,var(--bg-elevated) 100%)!important;}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]){border-left:3px solid var(--accent)!important;background:linear-gradient(135deg,rgba(56,189,248,.07) 0%,var(--bg-elevated) 100%)!important;}
[data-testid="stChatInputContainer"]{background:var(--bg-surface)!important;border-top:1px solid var(--border);padding:0.9rem 2rem!important;}
.stChatInput textarea,.stChatInput input,[data-testid="stChatInputContainer"] textarea,[data-testid="stChatInputContainer"] input,div[contenteditable="true"]{background:var(--bg-input)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius)!important;color:#f1f5f9!important;font-family:'Inter',sans-serif!important;font-size:0.95rem!important;caret-color:var(--accent)!important;}
.stChatInput textarea:focus,.stChatInput input:focus,[data-testid="stChatInputContainer"] textarea:focus,[data-testid="stChatInputContainer"] input:focus,div[contenteditable="true"]:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--glow)!important;outline:none!important;}
.stChatInput textarea::placeholder,.stChatInput input::placeholder,[data-testid="stChatInputContainer"] textarea::placeholder,[data-testid="stChatInputContainer"] input::placeholder{color:var(--text-muted)!important;opacity:1!important;}
.stButton>button{background:linear-gradient(135deg,#0ea5e9 0%,#6366f1 100%)!important;color:#fff!important;border:none!important;border-radius:var(--radius)!important;font-weight:600!important;font-size:0.9rem!important;padding:0.55rem 1.3rem!important;transition:all .2s ease!important;box-shadow:0 4px 20px rgba(14,165,233,.3)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(14,165,233,.45)!important;}
[data-testid="stSelectbox"]>div>div,[data-testid="stTextInput"]>div>div>input,[data-testid="stNumberInput"] input{background:var(--bg-input)!important;border-color:var(--border)!important;color:var(--text)!important;border-radius:var(--radius)!important;}
[data-testid="stExpander"]{border:1px solid var(--border)!important;border-radius:var(--radius)!important;background:var(--bg-elevated)!important;overflow:hidden;}
[data-testid="stExpander"] summary{color:var(--text)!important;font-weight:500!important;}
[data-testid="stMetric"]{background:linear-gradient(135deg,rgba(56,189,248,.06),rgba(129,140,248,.06))!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:0.8rem 1rem!important;text-align:center!important;}
[data-testid="stMetricValue"]{font-size:1.5rem!important;font-weight:800!important;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
[data-testid="stMetricLabel"]{font-size:0.72rem!important;color:var(--text-muted)!important;}
code,pre{font-family:'JetBrains Mono',monospace!important;background:rgba(56,189,248,.07)!important;color:var(--text-code)!important;border-radius:8px!important;border:1px solid rgba(56,189,248,.15)!important;}
.stSpinner>div{border-top-color:var(--accent)!important;}
.stProgress>div>div{background:linear-gradient(90deg,var(--accent),var(--accent2))!important;}
[data-testid="stAlert"]{border-radius:var(--radius)!important;border-left-width:4px!important;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 11px;border-radius:9999px;font-size:0.71rem;font-weight:600;letter-spacing:0.04em;}
.badge-green {background:rgba(52,211,153,.12);color:#34d399;border:1px solid rgba(52,211,153,.3);}
.badge-purple{background:rgba(129,140,248,.12);color:#818cf8;border:1px solid rgba(129,140,248,.3);}
.badge-yellow{background:rgba(251,191,36,.12); color:#fbbf24;border:1px solid rgba(251,191,36,.3);}
.badge-blue  {background:rgba(56,189,248,.12); color:#38bdf8;border:1px solid rgba(56,189,248,.3);}
hr{border-color:var(--border)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg-base);}
::-webkit-scrollbar-thumb{background:rgba(56,189,248,.35);border-radius:99px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state() -> None:
    defaults: dict = {
        "messages": [],           # list of {"role": str, "content": str}
        "chat_history": [],       # list of LangChain BaseMessages
        "library_filter": None,   # active library filter
        "pipeline": None,         # RAGPipeline singleton
        "last_sources": [],       # SearchResult list from last query
        "last_elapsed": 0.0,
        "last_model": "",
        "last_retrieved": 0,
        "ingestion_log": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


# ---------------------------------------------------------------------------
# Pipeline loader (lazy, cached)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_pipeline(library_filter: str | None = None):
    """Load the RAG pipeline (cached across reruns)."""
    from pipeline.rag_chain import RAGPipeline
    return RAGPipeline(library_filter=library_filter or None)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _render_sidebar() -> None:
    with st.sidebar:
        # Logo
        st.markdown(
            '<div class="docai-logo"><span>🤖</span><h1>DocAI</h1></div>',
            unsafe_allow_html=True,
        )

        # ── Knowledge base stats ───────────────────────────────────────────
        st.markdown('<p class="sidebar-section">📚 Knowledge Base</p>', unsafe_allow_html=True)
        doc_counts = count_documents()
        total_docs = sum(doc_counts.values())

        col1, col2 = st.columns(2)
        col1.metric("Libraries", len(doc_counts))
        col2.metric("Documents", total_docs)

        if doc_counts:
            for lib, count in sorted(doc_counts.items()):
                st.markdown(
                    f'<div class="source-card" style="padding:0.4rem 0.75rem;">'
                    f'<span class="badge badge-purple">{lib}</span>'
                    f'<span style="float:right;font-size:0.8rem;color:var(--text-muted)">{count} docs</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── Library filter ─────────────────────────────────────────────────
        st.markdown('<p class="sidebar-section">🔍 Filter</p>', unsafe_allow_html=True)
        lib_options = ["All libraries"] + sorted(doc_counts.keys())
        selected_lib = st.selectbox(
            "Search in:",
            lib_options,
            label_visibility="collapsed",
            key="lib_select",
        )
        st.session_state.library_filter = None if selected_lib == "All libraries" else selected_lib

        # ── Ingest new documentation ───────────────────────────────────────
        st.markdown('<p class="sidebar-section">⚡ Ingest Docs</p>', unsafe_allow_html=True)
        with st.expander("Crawl & Index New Documentation", expanded=False):
            ingest_url = st.text_input(
                "Documentation URL",
                placeholder="https://docs.example.com/",
                key="ingest_url",
            )
            col_a, col_b = st.columns(2)
            max_depth = col_a.number_input("Depth", 1, 10, 3, key="max_depth_in")
            max_pages = col_b.number_input("Max pages", 0, 500, 50, key="max_pages_in")

            if st.button("🚀 Start Ingestion", key="btn_ingest", use_container_width=True):
                if ingest_url:
                    _run_ingestion(ingest_url, int(max_depth), int(max_pages))
                else:
                    st.warning("Please enter a URL first.")

            if st.session_state.ingestion_log:
                st.divider()
                for entry in st.session_state.ingestion_log[-5:]:
                    st.markdown(
                        f'<p style="font-size:0.75rem;color:var(--text-muted);margin:2px 0">{entry}</p>',
                        unsafe_allow_html=True,
                    )

        # ── Settings summary ───────────────────────────────────────────────
        st.markdown('<p class="sidebar-section">⚙️ Config</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="source-card" style="font-size:0.78rem;">'
            f'🧠 <b>LLM:</b> {settings.llm_provider} / {settings.llm_model}<br>'
            f'🔢 <b>Embed:</b> {settings.embedding_model.split("/")[-1]}<br>'
            f'🗄️ <b>VectorDB:</b> {settings.vector_db_type}<br>'
            f'🔍 <b>Retrieval:</b> {settings.retrieval_method} · top-{settings.retrieval_top_k}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Clear chat ─────────────────────────────────────────────────────
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.last_sources = []
            st.rerun()


# ---------------------------------------------------------------------------
# Ingestion runner
# ---------------------------------------------------------------------------

def _run_ingestion(url: str, max_depth: int, max_pages: int) -> None:
    """Run the crawler + embed + index pipeline for a new documentation URL."""
    import traceback

    log = st.session_state.ingestion_log
    status_box = st.empty()

    # ── Step 1: Crawl ────────────────────────────────────────────────────
    status_box.info(f"🕷️ Crawling `{url}` …  (this may take 1–3 minutes, please wait)")
    try:
        from crawler.spider import DocumentationSpider

        spider = DocumentationSpider(
            start_url=url,
            max_depth=max_depth,
            max_pages=max_pages,
        )
        report = spider.run()
        msg = f"✅ Crawled {report.pages_crawled} pages from {url}"
        log.append(msg)
        status_box.success(msg)
    except Exception as exc:
        err = f"❌ Crawl failed: {exc}"
        log.append(err)
        status_box.error(f"Crawl failed: {exc}")
        return

    if report.pages_crawled == 0:
        status_box.warning(
            "⚠️ No pages were crawled. Tips:\n"
            "- Make sure the URL is publicly accessible\n"
            "- Try the docs index page directly (e.g. `https://docs.example.com/`)\n"
            "- Check your internet connection"
        )
        return

    # ── Step 2: Embed & index ────────────────────────────────────────────
    status_box.info(f"🔢 Embedding {report.pages_crawled} pages … (may take a few minutes)")
    try:
        _embed_knowledge_base()
        log.append("✅ Embedding and indexing complete.")
        status_box.success(
            f"🎉 Ingestion complete! **{report.pages_crawled} pages** indexed and ready to query."
        )
        # Clear pipeline cache so it reloads with new data.
        _load_pipeline.clear()
    except Exception as exc:
        err = f"❌ Embedding failed: {exc}"
        log.append(err)
        status_box.error(f"Embedding failed: {exc}\n\n{traceback.format_exc()}")



def _embed_knowledge_base() -> None:
    """Walk the knowledge base, chunk, embed, and store all documents."""
    from embeddings.embedder import get_embedder
    from preprocessing.chunker import chunk_document
    from preprocessing.cleaner import clean_document
    from preprocessing.metadata import build_chunk_metadata
    from vectordb.vector_store import get_vector_store
    from utils.helpers import list_knowledge_base, load_markdown_file, read_metadata_json

    store = get_vector_store()
    embedder = get_embedder()
    all_texts: list[str] = []
    all_metas: list[dict] = []

    for md_path, meta_path in list_knowledge_base():
        raw = load_markdown_file(md_path)
        base_meta = read_metadata_json(meta_path)
        cleaned = clean_document(raw)
        chunks = chunk_document(
            text=cleaned,
            source_url=base_meta.get("url", ""),
            library=base_meta.get("library", ""),
        )
        for chunk in chunks:
            meta = build_chunk_metadata(
                chunk=chunk,
                base_metadata=base_meta,
                source_file=str(md_path),
                embedding_model=settings.embedding_model,
            )
            all_texts.append(chunk.text)
            all_metas.append(meta)

    if all_texts:
        store.add_chunks(all_texts, all_metas)


# ---------------------------------------------------------------------------
# Main chat interface
# ---------------------------------------------------------------------------

def _render_chat() -> None:
    # Page title
    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <h1 style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#6c63ff,#a78bfa,#38bdf8);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;">
                Documentation Assistant
            </h1>
            <p style="color:var(--text-muted);margin:0.25rem 0 0;font-size:0.9rem;">
                Ask anything about your ingested documentation libraries
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Last query metadata bar ────────────────────────────────────────────
    if st.session_state.last_retrieved:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⏱ Response time", format_elapsed(st.session_state.last_elapsed))
        c2.metric("📦 Chunks used", st.session_state.last_retrieved)
        c3.metric("🧠 Model", st.session_state.last_model.split("-")[0] or "—")
        c4.metric("🔍 Method", settings.retrieval_method.upper())
        st.divider()

    # ── Chat history ───────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                _render_sources(msg["sources"])

    # ── Empty state prompt ─────────────────────────────────────────────────
    if not st.session_state.messages:
        _render_empty_state()

    # ── Chat input ─────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask anything about the documentation…", key="chat_input"):
        _handle_user_message(prompt)


def _render_empty_state() -> None:
    """Render the welcome / empty state."""
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:4rem;margin-bottom:1rem;">📖</div>
            <h2 style="font-weight:700;color:var(--text-primary);margin:0 0 0.5rem">
                Ask your documentation
            </h2>
            <p style="color:var(--text-muted);max-width:480px;margin:0 auto 2rem;">
                Ingest library docs using the sidebar, then ask questions in natural language.
                DocAI retrieves the exact passage and generates a grounded answer.
            </p>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.75rem;max-width:800px;margin:0 auto;">
    """,
        unsafe_allow_html=True,
    )

    example_questions = [
        ("🔗", "How do I create a LangChain chain?"),
        ("🔍", "What is Maximal Marginal Relevance?"),
        ("🗄️", "How does Chroma persist vector indexes?"),
        ("🤖", "Explain LangGraph StateGraph nodes"),
    ]
    cols = st.columns(len(example_questions))
    for col, (icon, q) in zip(cols, example_questions):
        with col:
            if st.button(f"{icon} {q}", key=f"example_{q[:20]}", use_container_width=True):
                _handle_user_message(q)

    st.markdown("</div>", unsafe_allow_html=True)


# Greeting keywords that should get an instant reply without the RAG pipeline
_GREETINGS = {
    "hi", "hello", "hey", "hiya", "howdy", "greetings",
    "good morning", "good afternoon", "good evening",
    "hi there", "hello there", "hey there",
}

_FAREWELLS = {
    "bye", "goodbye", "exit", "quit", "see ya", "cya",
}

def _is_greeting(text: str) -> bool:
    """Return True if the message is just a greeting."""
    return text.strip().lower().rstrip("!.,?") in _GREETINGS

def _is_farewell(text: str) -> bool:
    """Return True if the message is just a farewell."""
    return text.strip().lower().rstrip("!.,?") in _FAREWELLS


def _handle_user_message(prompt: str) -> None:
    """Process a user message: display it and stream the assistant reply."""
    # Display user message.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ── Greeting shortcut – no RAG pipeline needed ────────────────────────
    if _is_greeting(prompt):
        greeting_reply = (
            "Hello! 👋 Welcome to **DocAI** — your documentation assistant.\n\n"
            "I can answer questions about any documentation you've ingested. "
            "Try asking something like:\n"
            "- *What is LangChain?*\n"
            "- *How does ChromaDB persist vector indexes?*\n"
            "- *Explain LangGraph StateGraph nodes*\n\n"
            "How can I help you today?"
        )
        with st.chat_message("assistant"):
            st.markdown(greeting_reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting_reply, "sources": []}
        )
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        st.session_state.chat_history.append(AIMessage(content=greeting_reply))
        st.rerun()
        return

    if _is_farewell(prompt):
        farewell_reply = "Bye! 👋"
        with st.chat_message("assistant"):
            st.markdown(farewell_reply)
        st.session_state.messages.append(
            {"role": "assistant", "content": farewell_reply, "sources": []}
        )
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        st.session_state.chat_history.append(AIMessage(content=farewell_reply))
        st.rerun()
        return

    # ── Full RAG pipeline for real questions ─────────────────────────────
    with st.chat_message("assistant"):
        pipeline = _load_pipeline(st.session_state.library_filter)

        # Stream tokens.
        placeholder = st.empty()
        streamed = ""
        try:
            for token in pipeline.stream(
                question=prompt,
                chat_history=st.session_state.chat_history,
                library_filter=st.session_state.library_filter,
            ):
                streamed += token
                placeholder.markdown(streamed + "▌")
            placeholder.markdown(streamed)
        except Exception as exc:
            streamed = f"⚠️ Error generating response: {exc}"
            placeholder.markdown(streamed)

        # Also run the non-streaming path to get structured metadata.
        response = pipeline.ask(
            question=prompt,
            chat_history=st.session_state.chat_history,
            library_filter=st.session_state.library_filter,
        )

        # Use the streamed text for the answer (richer), but take metadata
        # from the structured response.
        sources = response.sources
        if sources:
            _render_sources(sources)

    # Update session state.
    st.session_state.messages.append(
        {"role": "assistant", "content": streamed, "sources": sources}
    )
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    st.session_state.chat_history.append(AIMessage(content=streamed))

    # Keep history bounded.
    if len(st.session_state.chat_history) > 20:
        st.session_state.chat_history = st.session_state.chat_history[-20:]

    # Store metadata for the top bar.
    st.session_state.last_elapsed = response.elapsed_seconds
    st.session_state.last_model = response.model
    st.session_state.last_retrieved = response.retrieved_count
    st.session_state.last_sources = sources

    st.rerun()


def _render_sources(sources: list) -> None:
    """Render an expandable sources / retrieved chunks panel."""
    if not sources:
        return

    with st.expander(
        f"📎 {len(sources)} source(s) retrieved",
        expanded=False,
    ):
        for i, src in enumerate(sources, start=1):
            score_pct = int(src.score * 100)
            score_color = (
                "badge-green" if score_pct >= 80
                else "badge-yellow" if score_pct >= 50
                else "badge-purple"
            )
            code_badge = (
                '<span class="badge badge-blue">⌨ code</span> '
                if src.has_code else ""
            )
            table_badge = (
                '<span class="badge badge-yellow">📊 table</span> '
                if src.has_table else ""
            )

            heading_label = truncate_text(src.heading or "No heading", 60)
            url = src.source_url or "#"
            library = src.library or "unknown"

            st.markdown(
                f"""
                <div class="source-card">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;">
                    <div>
                      <span class="badge badge-purple">{library}</span>
                      {code_badge}{table_badge}
                    </div>
                    <span class="badge {score_color} source-score">
                      {score_pct}% match
                    </span>
                  </div>
                  <div style="font-weight:600;font-size:0.85rem;margin-bottom:0.25rem;">
                    [{i}] {heading_label}
                  </div>
                  <div style="font-size:0.75rem;color:var(--text-muted);">
                    <a href="{url}" target="_blank" style="color:var(--accent);text-decoration:none;">
                      🔗 {url[:80]}{'…' if len(url) > 80 else ''}
                    </a>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"View chunk {i}", expanded=False):
                st.markdown(src.text)
                meta_display = {
                    k: v for k, v in src.metadata.items()
                    if k in ("id", "chunk_index", "word_count", "category", "topic", "tags")
                }
                st.json(meta_display)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    _render_sidebar()
    _render_chat()


if __name__ == "__main__":
    main()
