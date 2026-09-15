"""
Supabase access layer.

Only this module talks directly to Supabase. The database remains the persistence
layer; AI requests go directly from the backend to Sarvam.
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
    result = get_client().table("resumes").insert({"user_id": user_id, "filename": filename, "raw_text": raw_text, "parsed": parsed}).execute()
    return result.data[0]


def list_resumes(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    result = get_client().table("resumes").select("id, filename, parsed, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(max(1, min(limit, 100))).execute()
    return result.data


def get_resume(resume_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("resumes").select("*").eq("id", resume_id).eq("user_id", user_id).limit(1).execute()
    return result.data[0] if result.data else None


def delete_resume(resume_id: str, user_id: str) -> bool:
    result = get_client().table("resumes").delete().eq("id", resume_id).eq("user_id", user_id).execute()
    return bool(result.data)


# --- Jobs --------------------------------------------------------------------

def insert_job(title: str, company: str, skills: str, description: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
    row = {"title": title, "company": company, "skills": skills, "description": description}
    if embedding is not None:
        row["embedding"] = embedding
    result = get_client().table("jobs").insert(row).execute()
    return result.data[0]


def list_jobs() -> List[Dict[str, Any]]:
    result = get_client().table("jobs").select("id, title, company, skills, description, created_at").order("created_at", desc=True).execute()
    return result.data


def delete_job(job_id: str) -> None:
    get_client().table("jobs").delete().eq("id", job_id).execute()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("jobs").select("*").eq("id", job_id).limit(1).execute()
    return result.data[0] if result.data else None


def match_jobs(query_embedding: List[float], match_count: int) -> List[Dict[str, Any]]:
    result = get_client().rpc("match_jobs", {"query_embedding": query_embedding, "match_count": match_count}).execute()
    return result.data


def jobs_count() -> int:
    result = get_client().table("jobs").select("id", count="exact").execute()
    return result.count or 0


# --- Career notes ------------------------------------------------------------

def insert_career_note_chunks(chunks: List[Dict[str, Any]]) -> None:
    get_client().table("career_notes").insert(chunks).execute()


def list_career_notes() -> List[Dict[str, Any]]:
    result = get_client().table("career_notes").select("id, filename, chunk_index, content").order("filename").order("chunk_index").execute()
    return result.data


def delete_career_note(filename: str) -> None:
    get_client().table("career_notes").delete().eq("filename", filename).execute()


def match_career_notes(query_embedding: List[float], match_count: int) -> List[Dict[str, Any]]:
    result = get_client().rpc("match_career_notes", {"query_embedding": query_embedding, "match_count": match_count}).execute()
    return result.data


def career_notes_count() -> int:
    result = get_client().table("career_notes").select("id", count="exact").execute()
    return result.count or 0


# --- Chat sessions / messages -----------------------------------------------

def create_chat_session(user_id: str, title: str) -> Dict[str, Any]:
    result = get_client().table("chat_sessions").insert({"user_id": user_id, "title": title}).execute()
    return result.data[0]


def list_chat_sessions(user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
    result = get_client().table("chat_sessions").select("id, title, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(max(1, min(limit, 100))).execute()
    return result.data


def get_chat_session(session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("chat_sessions").select("*").eq("id", session_id).eq("user_id", user_id).limit(1).execute()
    return result.data[0] if result.data else None


def delete_chat_session(session_id: str, user_id: str) -> bool:
    result = get_client().table("chat_sessions").delete().eq("id", session_id).eq("user_id", user_id).execute()
    return bool(result.data)


def list_chat_messages(session_id: str) -> List[Dict[str, Any]]:
    result = get_client().table("chat_messages").select("*").eq("session_id", session_id).order("created_at").execute()
    return result.data


def insert_chat_message(session_id: str, role: str, content: str, sources: Optional[List[str]] = None, grounded: Optional[bool] = None, blocked: Optional[bool] = None) -> Dict[str, Any]:
    result = get_client().table("chat_messages").insert({"session_id": session_id, "role": role, "content": content, "sources": sources or [], "grounded": grounded, "blocked": blocked}).execute()
    return result.data[0]


# --- CV suggestion history --------------------------------------------------

def insert_cv_suggestion(resume_id: str, job_id: Optional[str], kind: str, content: str) -> Dict[str, Any]:
    result = get_client().table("cv_suggestions").insert({"resume_id": resume_id, "job_id": job_id, "kind": kind, "content": content}).execute()
    return result.data[0]


def list_cv_suggestions(resume_id: str, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    resume = get_resume(resume_id, user_id)
    if resume is None:
        return []
    result = get_client().table("cv_suggestions").select("id, resume_id, job_id, kind, content, created_at").eq("resume_id", resume_id).order("created_at", desc=True).limit(max(1, min(limit, 100))).execute()
    return result.data


# --- Profiles ---------------------------------------------------------------

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    result = get_client().table("profiles").select("*").eq("id", user_id).limit(1).execute()
    return result.data[0] if result.data else None
