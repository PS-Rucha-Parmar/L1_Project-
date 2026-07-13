import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.logging_config import setup_logging
from config.settings import settings

setup_logging(log_level=settings.log_level)

def test_embed():
    from ui.app import _embed_knowledge_base
    print("--- Embedding Knowledge Base ---")
    _embed_knowledge_base()
    print("Embedding complete.\n")

def test_retrieval():
    from pipeline.rag_chain import RAGPipeline
    print("--- Testing Retrieval ---")
    pipeline = RAGPipeline()
    response = pipeline.ask("How do I create an API key?")
    print(f"Retrieved {response.retrieved_count} documents.")
    for i, s in enumerate(response.sources):
        print(f"Source {i+1}: {s.source_url} (Score: {s.score})")
    print("\nAnswer:")
    print(response.answer)

if __name__ == "__main__":
    test_embed()
    test_retrieval()
