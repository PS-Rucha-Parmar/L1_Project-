"""
prompts/__init__.py
"""
from prompts.templates import (
    RAG_CHAT_PROMPT,
    CONDENSE_PROMPT,
    NO_CONTEXT_RESPONSE,
    format_context,
)

__all__ = [
    "RAG_CHAT_PROMPT",
    "CONDENSE_PROMPT",
    "NO_CONTEXT_RESPONSE",
    "format_context",
]
