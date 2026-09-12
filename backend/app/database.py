"""
Supabase access layer.

Responsibility: the only module that talks to Supabase directly. Uses the
SERVICE ROLE key (server-side only, never exposed to the frontend) so the
backend can read/write across all users' data as needed for its endpoints;
Postgres Row Level Security still protects the tables from any direct
client access that bypasses this backend (e.g. the frontend's own anon-key
Supabase calls for auth and profile lookups).
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from app.config import settings


@lru_cache(maxsize=1)
def get_client() -> Client:
    settings.require_supabase()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# --- Resumes -----------------------------------------------------------------

def insert_resume(user_id: str, filename: str, raw_text: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    result = (
        get_client()
        .table("resumes")
        .insert({"user_id": user_id, "filename": filename, "raw_text": raw_text, "parsed": parsed})
        .execute()
    )
    return result.data[0]


def get_resume(resume_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    result = (
        get_client()
        .table("resumes")
        .select("*")
        .eq("id", resume_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


# --- Jobs ----------------------------------------------------------------------

def insert_job(title: str, company: str, skills: str, description: str, embedding: List[float]) -> Dict[str, Any]:
    result = (
        get_client()
        .table("jobs")
        .insert(
            {
                "title": title,
                "company": company,
                "skills": skills,
                "description": description,
                "embedding": embedding,
            }
        )
        .execute()
    )
    return result.data[0]


def list_jobs() -> List[Dict[str, Any]]:
    result = get_client().table("jobs").select("id, title, company, skills, description, created_at").order(
        "created_at", desc=True
    ).execute()
    return result.data


def delete_job(job_id: str) -> None:
    get_client().table("jobs").delete().eq("id", job_id).execute()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("jobs").select("*").eq("id", job_id).limit(1).execute()
    return result.data[0] if result.data else None


def match_jobs(query_embedding: List[float], match_count: int) -> List[Dict[str, Any]]:
    """Calls the match_jobs() Postgres function (supabase/migrations/0002_functions.sql)."""
    result = get_client().rpc(
        "match_jobs", {"query_embedding": query_embedding, "match_count": match_count}
    ).execute()
    return result.data


def jobs_count() -> int:
    result = get_client().table("jobs").select("id", count="exact").execute()
    return result.count or 0


# --- Career notes ----------------------------------------------------------------

def insert_career_note_chunks(chunks: List[Dict[str, Any]]) -> None:
    """chunks: list of {"filename", "chunk_index", "content", "embedding"}."""
    get_client().table("career_notes").insert(chunks).execute()


def list_career_notes() -> List[Dict[str, Any]]:
    result = (
        get_client()
        .table("career_notes")
        .select("id, filename, chunk_index, content")
        .order("filename")
        .order("chunk_index")
        .execute()
    )
    return result.data


def delete_career_note(filename: str) -> None:
    get_client().table("career_notes").delete().eq("filename", filename).execute()


def match_career_notes(query_embedding: List[float], match_count: int) -> List[Dict[str, Any]]:
    """Calls the match_career_notes() Postgres function."""
    result = get_client().rpc(
        "match_career_notes", {"query_embedding": query_embedding, "match_count": match_count}
    ).execute()
    return result.data


def career_notes_count() -> int:
    result = get_client().table("career_notes").select("id", count="exact").execute()
    return result.count or 0


# --- Chat sessions / messages -----------------------------------------------------

def create_chat_session(user_id: str, title: str) -> Dict[str, Any]:
    result = get_client().table("chat_sessions").insert({"user_id": user_id, "title": title}).execute()
    return result.data[0]


def get_chat_session(session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    result = (
        get_client()
        .table("chat_sessions")
        .select("*")
        .eq("id", session_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_chat_messages(session_id: str) -> List[Dict[str, Any]]:
    result = (
        get_client()
        .table("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return result.data


def insert_chat_message(
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[str]] = None,
    grounded: Optional[bool] = None,
    blocked: Optional[bool] = None,
) -> Dict[str, Any]:
    result = (
        get_client()
        .table("chat_messages")
        .insert(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
                "sources": sources or [],
                "grounded": grounded,
                "blocked": blocked,
            }
        )
        .execute()
    )
    return result.data[0]


# --- CV suggestions cache -----------------------------------------------------

def insert_cv_suggestion(resume_id: str, job_id: Optional[str], kind: str, content: str) -> Dict[str, Any]:
    result = (
        get_client()
        .table("cv_suggestions")
        .insert({"resume_id": resume_id, "job_id": job_id, "kind": kind, "content": content})
        .execute()
    )
    return result.data[0]


# --- Profiles ------------------------------------------------------------------

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("profiles").select("*").eq("id", user_id).limit(1).execute()
    return result.data[0] if result.data else None
