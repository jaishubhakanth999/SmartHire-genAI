"""
Embeddings and FAISS index management.

Responsibility: the vector layer. Turn text into vectors (locally, via a free
sentence-transformers model -- no API key or per-call cost), build a FAISS
index from a set of documents, persist it to disk, and load it back. This is
the only module that talks to FAISS / the embeddings model directly; every
other module goes through search_jobs() or the mentor's retriever instead.
"""

from pathlib import Path
from typing import Any, Dict, List, Union

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import load_config

PathLike = Union[str, Path]

_embeddings = None  # lazy singleton -- loading the model has real cost/latency


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return the configured (local, free) embeddings model."""
    global _embeddings
    if _embeddings is None:
        config = load_config()
        _embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model)
    return _embeddings


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of strings into vectors."""
    if not texts:
        return []
    return get_embeddings().embed_documents(texts)


def _to_documents(documents: List[Dict[str, Any]]) -> List[Document]:
    return [Document(page_content=d["text"], metadata=d.get("metadata", {})) for d in documents]


def build_index(documents: List[Dict[str, Any]], persist_dir: PathLike) -> FAISS:
    """
    Build a FAISS index from {"text", "metadata"} documents and persist it.

    Raises:
        ValueError: if `documents` is empty -- an empty index is never what
            you want and silently building one hides a data-loading bug.
    """
    if not documents:
        raise ValueError("Cannot build an index from zero documents.")
    persist_dir = Path(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    lc_documents = _to_documents(documents)
    index = FAISS.from_documents(lc_documents, get_embeddings())
    index.save_local(str(persist_dir))
    return index


def load_index(persist_dir: PathLike) -> FAISS:
    """Load a previously persisted FAISS index."""
    persist_dir = Path(persist_dir)
    if not index_exists(persist_dir):
        raise FileNotFoundError(
            f"No FAISS index at '{persist_dir}'. Build one first (see "
            "src/search/job_search.py build_job_index() or "
            "notebooks/02_build_faiss.ipynb)."
        )
    # allow_dangerous_deserialization: safe here because we only ever load
    # indexes this same project built, never one from an untrusted source.
    return FAISS.load_local(str(persist_dir), get_embeddings(), allow_dangerous_deserialization=True)


def index_exists(persist_dir: PathLike) -> bool:
    """Check whether a persisted index is already present."""
    persist_dir = Path(persist_dir)
    return (persist_dir / "index.faiss").exists() and (persist_dir / "index.pkl").exists()
