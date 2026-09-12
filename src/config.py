"""
Central configuration for SmartHire GenAI.

Single source of truth for paths, model names and retrieval settings.
Everything is read from environment variables (see .env.example) so that no
secret or environment-specific value is ever hardcoded in a module.

Every other module imports from here rather than calling os.getenv directly.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load variables from a .env file in the project root (if one exists).
# Safe to call even when there is no .env yet -- it just does nothing.
load_dotenv()

# Local, free, no-API-key embedding model. Kept as a code default (not read
# from .env) because it is a stable open-source model id, not something that
# goes stale the way a hosted LLM model name can.
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass(frozen=True)
class Config:
    # --- Paths ---
    data_dir: Path
    jobs_dir: Path
    resumes_dir: Path
    career_notes_dir: Path
    vectorstore_dir: Path

    # --- LLM ---
    llm_api_key: Optional[str]
    llm_model: Optional[str]

    # --- Embeddings ---
    embedding_model: str

    # --- Retrieval ---
    chunk_size: int
    chunk_overlap: int
    top_k: int

    def require_llm(self) -> None:
        """
        Raise a clear error if the app is not configured to call an LLM.

        Call this at the top of any function that is about to make an LLM
        call (resume parsing, CV suggestions, the mentor). Loading config
        itself never fails just because the LLM isn't set up yet, since
        plenty of work (document loading, embeddings) doesn't need it.
        """
        if not self.llm_api_key:
            raise ValueError(
                "LLM_API_KEY is not set. Copy .env.example to .env and fill "
                "in your Sarvam AI API key (from https://dashboard.sarvam.ai)."
            )
        if not self.llm_model:
            raise ValueError(
                "LLM_MODEL is not set in .env. Pick a current Sarvam AI model "
                "id from https://docs.sarvam.ai/api/getting-started/models "
                "(e.g. 'sarvam-105b') and set LLM_MODEL to it."
            )


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Environment variable {name}='{raw}' is not a valid integer.")


def load_config() -> Config:
    """
    Read environment variables (from .env, loaded above) and return a
    validated Config object.

    Raises:
        ValueError: if a numeric retrieval setting is not a valid integer,
            if CHUNK_OVERLAP >= CHUNK_SIZE, or if a required data directory
            does not exist on disk (run this from the project root).
    """
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    vectorstore_dir = Path(os.getenv("VECTORSTORE_DIR", "vectorstore"))

    jobs_dir = data_dir / "jobs"
    resumes_dir = data_dir / "resumes"
    career_notes_dir = data_dir / "career_notes"

    for required_dir in (data_dir, jobs_dir, resumes_dir, career_notes_dir):
        if not required_dir.exists():
            raise ValueError(
                f"Expected data directory '{required_dir}' does not exist. "
                "Run this from the project root, or check DATA_DIR in .env."
            )

    chunk_size = _get_int("CHUNK_SIZE", 1000)
    chunk_overlap = _get_int("CHUNK_OVERLAP", 200)
    top_k = _get_int("TOP_K", 5)

    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"CHUNK_OVERLAP ({chunk_overlap}) must be smaller than CHUNK_SIZE ({chunk_size})."
        )
    if top_k < 1:
        raise ValueError(f"TOP_K ({top_k}) must be at least 1.")

    return Config(
        data_dir=data_dir,
        jobs_dir=jobs_dir,
        resumes_dir=resumes_dir,
        career_notes_dir=career_notes_dir,
        vectorstore_dir=vectorstore_dir,
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        llm_model=os.getenv("LLM_MODEL") or None,
        embedding_model=os.getenv("EMBEDDING_MODEL") or DEFAULT_EMBEDDING_MODEL,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
    )
