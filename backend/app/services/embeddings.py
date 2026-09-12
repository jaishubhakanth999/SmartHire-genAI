"""
Embeddings.

Responsibility: turn text into vectors using a local, free sentence-transformers
model -- no API key or per-call cost. Vector storage and similarity search
live in Postgres/pgvector (see app/database.py's match_jobs / match_career_notes
RPCs), not here; this module only produces the vectors.
"""

from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_text(text: str) -> List[float]:
    """Embed a single string into a vector (list of floats, JSON-serialisable)."""
    return get_model().encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of strings."""
    if not texts:
        return []
    return get_model().encode(texts, normalize_embeddings=True).tolist()
