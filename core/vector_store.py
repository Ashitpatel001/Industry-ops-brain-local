"""
core/vector_store.py
====================
In-process ChromaDB vector store using SQLite backend.
Zero server overhead, 100% offline persistence, optimized cosine similarity search.
"""

import logging
from typing import List, Dict, Any, Optional
from core.config import get_config

logger = logging.getLogger("VectorStore")


class VectorStore:
    """
    In-process ChromaDB vector store wrapper.
    Stores chunk embeddings and metadata in an embedded SQLite database.
    """

    def __init__(self, chroma_dir: Optional[str] = None, collection_name: str = "ops_brain_local"):
        cfg = get_config()
        self.chroma_dir = str(chroma_dir or cfg.chroma_dir)
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            logger.info(f"Initializing ChromaDB PersistentClient at {self.chroma_dir}...")
            self.client = chromadb.PersistentClient(path=self.chroma_dir)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB collection '{self.collection_name}' ready.")
        except ImportError as e:
            logger.warning(f"ChromaDB not installed yet ({e}). Please run: pip install -r requirements.txt. Operating in dry-run mode.")
            self.client = None
            self.collection = None
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        doc_id: str,
        tenant_id: Optional[str] = None,
    ):
        """
        Add document chunks to the ChromaDB collection.
        Each chunk dict should contain: {'chunk_id': str, 'text': str, 'vector': List[float], 'metadata': dict}
        """
        if not chunks:
            return

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for c in chunks:
            cid = c.get("chunk_id")
            text = c.get("text")
            vec = c.get("vector")
            if not cid or not text or not vec:
                continue

            ids.append(str(cid))
            documents.append(str(text))
            embeddings.append(vec)

            meta = c.get("metadata", {}).copy()
            meta["doc_id"] = str(doc_id)
            if tenant_id:
                meta["tenant_id"] = str(tenant_id)
            metadatas.append(meta)

        if not ids:
            return

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.debug(f"Upserted {len(ids)} chunks for doc_id='{doc_id}' into ChromaDB.")

    def search(
        self,
        query_vec: List[float],
        n_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for top-k nearest chunks by cosine similarity.
        Returns list of dicts with keys: chunk_id, text, metadata, score, doc_id.
        """
        if not self.collection:
            return []

        count = self.collection.count()
        if count == 0:
            return []

        actual_n = min(n_results, count)
        kwargs = {
            "query_embeddings": [query_vec],
            "n_results": actual_n,
            "include": ["documents", "metadatas", "distances"],
        }
        if filters:
            kwargs["where"] = filters

        try:
            res = self.collection.query(**kwargs)
        except Exception as e:
            logger.warning(f"ChromaDB search query failed: {e}")
            return []

        results = []
        if res and res.get("ids") and res["ids"][0]:
            for i in range(len(res["ids"][0])):
                meta = res["metadatas"][0][i] or {}
                dist = res["distances"][0][i] if res.get("distances") else 0.0
                # Convert cosine distance to similarity score in [0, 1]
                score = round(max(0.0, 1.0 - dist), 4)
                
                results.append({
                    "chunk_id": res["ids"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": meta,
                    "score": score,
                    "doc_id": meta.get("doc_id", ""),
                })
        return results

    def delete_doc(self, doc_id: str):
        """Delete all indexed chunks associated with a specific document ID."""
        if not self.collection:
            return
        try:
            self.collection.delete(where={"doc_id": doc_id})
            logger.info(f"Deleted chunks for doc_id='{doc_id}' from ChromaDB.")
        except Exception as e:
            logger.warning(f"Failed to delete doc_id='{doc_id}': {e}")

    def get_stats(self) -> Dict[str, int]:
        """Return statistics on indexed chunks and documents."""
        if not self.collection:
            return {"chunk_count": 0, "doc_count": 0}

        count = self.collection.count()
        doc_count = 0
        if count > 0:
            try:
                res = self.collection.get(include=["metadatas"])
                all_meta = res.get("metadatas", [])
                doc_ids = {m.get("doc_id") for m in all_meta if m and "doc_id" in m}
                doc_count = len(doc_ids)
            except Exception:
                doc_count = 1 if count > 0 else 0

        return {"chunk_count": count, "doc_count": doc_count}
