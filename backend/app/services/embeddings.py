"""
Embeddings.

Responsibility: turn text into vectors using a local, free embedding model --
no API key or per-call cost. Uses `fastembed` (ONNX Runtime) rather than
`sentence-transformers`/PyTorch: same model family and output dimension
(384-d, matching the vector(384) columns in supabase/migrations), but a much
smaller install and memory footprint -- important for fitting comfortably on
Render's free/starter instance sizes. Vector storage and similarity search
live in Postgres/pgvector (see app/database.py's match_jobs / match_career_notes
RPCs), not here; this module only produces the vectors.
"""

from typing import List

from fastembed import TextEmbedding

from app.config import settings

_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=settings.embedding_model)
    return _model


def embed_text(text: str) -> List[float]:
    """Embed a single string into a vector (list of floats, JSON-serialisable)."""
    return next(get_model().embed([text])).tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of strings."""
    if not texts:
        return []
    return [v.tolist() for v in get_model().embed(texts)]
