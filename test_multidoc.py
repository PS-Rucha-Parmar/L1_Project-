"""
End-to-end test: hybrid retrieval + multi-hop + multi-doc synthesis.
Run: .venv/bin/python test_multidoc.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.logging_config import setup_logging
from config.settings import settings
setup_logging(log_level="INFO")

def banner(text):
    print("\n" + "═" * 60)
    print(f"  {text}")
    print("═" * 60)

def test_hybrid_retrieval():
    banner("1. Building BM25 index")
    from retrieval.hybrid_retriever import get_hybrid_retriever
    retriever = get_hybrid_retriever()
    retriever._bm25.build()
    print(f"   BM25 index built: {retriever._bm25._built}")
    print(f"   Documents in index: {len(retriever._bm25._docs)}")

    banner("2. Hybrid retrieval test")
    results = retriever.retrieve(
        query="How do I create an API key?",
        k=8,
        rerank=True,
        expand_context=True,
    )
    print(f"   Results returned: {len(results)}")
    for i, r in enumerate(results, 1):
        expanded = "(expanded)" if r.metadata.get("_expanded") else ""
        hierarchy = " › ".join(r.section_hierarchy) if r.section_hierarchy else r.heading
        print(f"   [{i}] score={r.score:.4f} {expanded}")
        print(f"       Hierarchy: {hierarchy}")
        print(f"       URL: {r.source_url}")
        print(f"       Preview: {r.text[:80].replace(chr(10), ' ')}...")

def test_pipeline():
    banner("3. Full RAG pipeline – simple question")
    from pipeline.rag_chain import RAGPipeline
    pipeline = RAGPipeline()

    response = pipeline.ask("How do I create a Groq API key and make my first API call?")
    print(f"\n   Question: How do I create a Groq API key and make my first API call?")
    print(f"   Hops used: {response.hops_used}")
    print(f"   Retrieved: {response.retrieved_count} chunks")
    print(f"   Elapsed: {response.elapsed_seconds:.2f}s")
    print(f"\n--- ANSWER ---\n{response.answer}")
    print(f"\n--- SOURCES ---")
    for i, s in enumerate(response.sources, 1):
        print(f"  [{i}] {s.source_url} (score={s.score:.4f})")

if __name__ == "__main__":
    test_hybrid_retrieval()
    test_pipeline()
    print("\n✅ All tests complete.")
