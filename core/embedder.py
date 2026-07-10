"""
core/embedder.py
================
Local embedding engine using all-MiniLM-L6-v2 (384 dimensions).
Runs 100% offline on CPU with high throughput (~20k sentences/sec).
"""

import logging
from typing import List, Union
from core.config import get_config

logger = logging.getLogger("LocalEmbedder")


class LocalEmbedder:
    """
    Local embedding wrapper using all-MiniLM-L6-v2 (384 dimensions).
    Provides high-speed vector generation for document indexing and RAG queries.
    """

    def __init__(self, model_name: str = None):
        cfg = get_config()
        self.model_name = model_name or cfg.embed_model
        self._model = None
        self._load()

    def _load(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("Embedding model loaded successfully.")
        except ImportError as e:
            logger.error(f"Failed to import sentence_transformers: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading embedding model '{self.model_name}': {e}")
            raise

    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Embed a list of text strings into 384-dimensional normalized vectors.
        """
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            return []

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query string into a 384-dimensional vector.
        """
        if not text:
            return [0.0] * 384
        return self.embed([text])[0]
