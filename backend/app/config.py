"""
Central configuration for the SmartHire GenAI backend.

Single source of truth for env-driven settings. Every other module imports
from here rather than calling os.getenv directly, so all required
configuration is validated in one place at startup.
"""

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSIONS = 384
DEFAULT_LLM_MODEL = "sarvam-105b"


@dataclass(frozen=True)
class Settings:
    # --- Supabase ---
    supabase_url: str
    supabase_service_role_key: str
    # Kept for backwards compatibility with existing Render environment settings.
    # Authentication no longer depends on the legacy JWT secret.
    supabase_jwt_secret: str

    # --- LLM (Sarvam AI) ---
    llm_api_key: Optional[str]
    llm_model: Optional[str]

    # --- Embeddings ---
    embedding_model: str

    # --- Retrieval ---
    chunk_size: int
    chunk_overlap: int
    top_k: int

    # --- CORS ---
    cors_origins: List[str]

    def require_llm(self) -> None:
        if not self.llm_api_key:
            raise RuntimeError(
                "Sarvam AI is not configured. Set LLM_API_KEY (or the legacy "
                "SARVAM_API_KEY) in the backend environment."
            )
        if not self.llm_model:
            raise RuntimeError(
                "LLM_MODEL is not configured. The backend default is sarvam-105b."
            )

    def require_supabase(self) -> None:
        if not self.supabase_url or not self.supabase_service_role_key:
            raise RuntimeError(
                "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set. Create a Supabase "
                "project, run the migrations in supabase/migrations/, and fill in "
                "backend/.env from backend/.env.example."
            )


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Environment variable {name}='{raw}' is not a valid integer.")


def _first_env(*names: str) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def get_settings() -> Settings:
    chunk_size = _get_int("CHUNK_SIZE", 1000)
    chunk_overlap = _get_int("CHUNK_OVERLAP", 200)
    top_k = _get_int("TOP_K", 5)

    if chunk_overlap >= chunk_size:
        raise ValueError(f"CHUNK_OVERLAP ({chunk_overlap}) must be smaller than CHUNK_SIZE ({chunk_size}).")
    if top_k < 1:
        raise ValueError(f"TOP_K ({top_k}) must be at least 1.")

    cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()]

    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        llm_api_key=_first_env("LLM_API_KEY", "SARVAM_API_KEY"),
        llm_model=_first_env("LLM_MODEL", "SARVAM_MODEL") or DEFAULT_LLM_MODEL,
        embedding_model=os.getenv("EMBEDDING_MODEL") or DEFAULT_EMBEDDING_MODEL,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
        cors_origins=cors_origins,
    )


settings = get_settings()
