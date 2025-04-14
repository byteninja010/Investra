"""
ChromaDB Vector Store implementation for Financial RAG.

Provides persistent local vector storage and retrieval for sector reports,
market dynamics, and stock research documents.
"""

import os
import chromadb
from chromadb.config import Settings
from typing import Any

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")


class FinancialVectorStore:
    """Manages local ChromaDB storage and similarity search for finance documents."""

    def __init__(self, collection_name: str = "financial_research"):
        self.collection_name = collection_name
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Financial reports, sector analysis, and macro insights"}
        )

    def add_documents(self, documents: list[str], metadatas: list[dict[str, Any]], ids: list[str]):
        """Add or update documents in the vector store."""
        if not documents:
            return
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def search(self, query: str, n_results: int = 4, where: dict | None = None) -> list[dict[str, Any]]:
        """Search for relevant documents matching the query."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
            
            actual_n = min(n_results, count)
            results = self.collection.query(
                query_texts=[query],
                n_results=actual_n,
                where=where,
            )

            docs = []
            if results and results.get("documents") and results["documents"][0]:
                for doc, meta, doc_id in zip(
                    results["documents"][0],
                    results["metadatas"][0] if results.get("metadatas") else [{}] * len(results["documents"][0]),
                    results["ids"][0] if results.get("ids") else [""] * len(results["documents"][0]),
                ):
                    docs.append({
                        "id": doc_id,
                        "content": doc,
                        "metadata": meta,
                        "source": meta.get("source", "ChromaDB Knowledge Base"),
                        "title": meta.get("title", doc_id),
                        "sector": meta.get("sector", "General"),
                    })
            return docs
        except Exception as e:
            print(f"[VectorStore] Search error: {e}")
            return []

    def count(self) -> int:
        """Return total document count."""
        return self.collection.count()


# Singleton instance
_store = None

def get_vector_store() -> FinancialVectorStore:
    global _store
    if _store is None:
        _store = FinancialVectorStore()
    return _store
