"""
prompts/templates.py
--------------------
Prompt templates for the multi-document RAG pipeline.

Purpose       : Centralise all LangChain prompt templates so they can be
                tuned without touching business logic.

Templates
---------
    RAG_SYSTEM_PROMPT      – system instruction for multi-doc synthesis
    RAG_CHAT_PROMPT        – full chat prompt (system + history + human)
    CONDENSE_PROMPT        – standalone-question condenser for multi-turn chat
    MULTI_HOP_PROMPT       – sub-query generator for the multi-hop node
    NO_CONTEXT_RESPONSE    – canned reply when retrieval returns nothing

Dependencies  : langchain-core
"""

from __future__ import annotations

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

# ---------------------------------------------------------------------------
# RAG System Prompt – multi-document synthesis
# ---------------------------------------------------------------------------

RAG_SYSTEM_PROMPT = """\
You are **DocAI**, an expert documentation assistant that synthesises \
information across multiple retrieved documentation sources to produce \
comprehensive, accurate, and fully-cited answers.

## Conversational Behavior
- **Greetings:** If the user greets you (e.g., "Hi", "Hello", "Hey"), respond \
naturally and politely before offering assistance. (e.g., "Hello! 👋 Welcome to \
DocAI. How can I help you today?")
- **Tone:** Maintain a professional, friendly, and respectful tone. Avoid \
robotic or overly technical wording unless specifically requested. Use natural \
conversational language while remaining concise.
- **Structure:** Use short paragraphs or bullet points when appropriate to \
ensure clear responses. Combine information into one coherent answer instead \
of listing disconnected snippets.
- **Closing:** End your responses naturally when appropriate. Examples: \
"Let me know if you'd like me to explain this in more detail.", \
"Feel free to ask another question.", or "I'm happy to help with anything else."

## Core Rules
1. Answer **only** using the information in the Retrieved Sources below.
2. **Synthesise** across ALL relevant sources – do not just quote one chunk.
3. When multiple sources **agree**, state the fact confidently and cite all of them.
4. When sources **conflict or differ**, present both perspectives clearly and \
note the discrepancy (e.g. "Source [1] states X, while Source [3] states Y").
5. If the retrieved context contains a SYSTEM NOTE about missing documents, \
do not attempt to answer the technical question. Instead, provide the \
appropriate message below (you may prepend a greeting if the user said hello):
   - **Empty DB:** "I couldn't find any indexed documents in the knowledge base yet. It looks like the relevant documentation hasn't been ingested. Please ingest the required documents and try again."
   - **No Match:** "I searched the available documentation but couldn't find information related to your question. You may want to rephrase your query or ingest additional documentation."
6. **Never** fabricate information, invent APIs, method names, or parameters.
7. Cite every factual claim inline using [1], [2], etc. matching the source \
numbers in Retrieved Sources.
8. Preserve all code examples **exactly** as they appear – do not modify them.
9. Format your response in clean, well-structured Markdown with headings, \
bullet points, and code blocks where appropriate.
10. End every response with a **## References** section listing only the \
sources you actually cited, in the format:
    > **[N]** *Heading* — [url](url) (`library`)

## Multi-Document Reasoning Guidelines
- Look for **complementary** information: one source may define a concept while \
another shows the code; combine both in your answer.
- Look for **sequential** information: if sources cover steps of a workflow, \
present them in order.
- When a fact appears in only ONE source, prefix with "According to [N]…"
- When confirmed by MULTIPLE sources, you may state it directly and list all \
citations.

## Retrieved Sources
{context}
"""

RAG_HUMAN_TEMPLATE = "{question}"

# ---------------------------------------------------------------------------
# Full RAG chat prompt (system + optional history + human)
# ---------------------------------------------------------------------------

RAG_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(RAG_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate.from_template(RAG_HUMAN_TEMPLATE),
    ]
)

# ---------------------------------------------------------------------------
# Standalone question condenser
# ---------------------------------------------------------------------------

CONDENSE_SYSTEM = """\
Given the following conversation and a follow-up question, rephrase the \
follow-up question to be a fully self-contained standalone question that \
captures all relevant context from the conversation history.

Return ONLY the rephrased question with no additional explanation.\
"""

CONDENSE_HUMAN = """\
Chat History:
{chat_history}

Follow-up Question: {question}

Standalone Question:\
"""

CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", CONDENSE_SYSTEM),
        ("human", CONDENSE_HUMAN),
    ]
)

# ---------------------------------------------------------------------------
# Multi-hop sub-query generator
# ---------------------------------------------------------------------------

MULTI_HOP_SYSTEM = """\
You are a search query specialist. Given an original question and a summary \
of retrieved documentation that is insufficient to fully answer it, generate \
a single focused follow-up search query that targets the missing information.

Rules:
- Return ONLY the search query – no explanation, no preamble.
- Make the query specific and different from the original question.
- Focus on the gap between what was found and what is needed.\
"""

MULTI_HOP_HUMAN = """\
Original question: {question}

Retrieved context so far (insufficient):
{context_summary}

What specific follow-up query would retrieve the missing information?\
"""

MULTI_HOP_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", MULTI_HOP_SYSTEM),
        ("human", MULTI_HOP_HUMAN),
    ]
)

# ---------------------------------------------------------------------------
# No-context fallback response
# ---------------------------------------------------------------------------

NO_CONTEXT_RESPONSE = (
    "I couldn't find this information in the indexed documentation. "
    "Please try rephrasing your question, or ingest the relevant documentation first."
)

# ---------------------------------------------------------------------------
# Context formatter – multi-source, hierarchical
# ---------------------------------------------------------------------------

def format_context(results: list, db_count: int = -1) -> str:
    """
    Format a list of :class:`~retrieval.searcher.SearchResult` objects into
    the numbered context block injected into the RAG prompt.

    Each source is numbered [N] and shows:
      - Section hierarchy breadcrumb  (library › category › topic › heading)
      - Source URL
      - Relevance score  (and a *(context)* tag if it was an expanded chunk)
      - The chunk text

    Args:
        results: List of SearchResult objects.
        db_count: Total documents in the vector DB (used for empty DB detection).

    Returns:
        Formatted multi-source context string, or a SYSTEM NOTE.
    """
    if not results:
        if db_count == 0:
            return "[SYSTEM NOTE: The vector database is empty. Provide the Empty DB message.]"
        return "[SYSTEM NOTE: The vector database has documents, but no matches were found. Provide the No Match message.]"

    sections: list[str] = []

    for i, result in enumerate(results, start=1):
        # Section hierarchy breadcrumb
        hierarchy = getattr(result, "section_hierarchy", [])
        if not hierarchy:
            parts = [
                x for x in [
                    result.library, result.category, result.topic, result.heading
                ] if x
            ]
            hierarchy = parts

        breadcrumb = " › ".join(hierarchy) if hierarchy else result.heading or "Documentation"
        url = result.source_url or "#"
        score = f"{result.score:.3f}"
        is_expanded = result.metadata.get("_expanded", False)
        expanded_tag = "  *(adjacent context)*" if is_expanded else ""

        # Content-type badges
        badges: list[str] = []
        if result.has_code:
            badges.append("💻 code")
        if result.has_table:
            badges.append("📊 table")
        badge_str = "  " + " · ".join(badges) if badges else ""

        header = (
            f"### [{i}] {breadcrumb}{expanded_tag}\n"
            f"**URL:** <{url}>  |  **Relevance:** `{score}`{badge_str}"
        )
        sections.append(f"{header}\n\n{result.text}")

    return "\n\n---\n\n".join(sections)
