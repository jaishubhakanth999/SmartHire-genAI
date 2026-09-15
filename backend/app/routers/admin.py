"""Admin endpoints for jobs and optional career notes."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, require_admin
from app.config import settings
from app.database import (
    career_notes_count,
    delete_career_note,
    delete_job,
    insert_career_note_chunks,
    insert_job,
    jobs_count,
    list_career_notes,
    list_jobs,
)
from app.schemas import AdminCareerNoteIn, AdminJobIn
from app.services.loader import chunk_text

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/jobs")
async def admin_list_jobs(_: CurrentUser = Depends(require_admin)):
    return {"jobs": list_jobs()}


@router.post("/jobs", status_code=201)
async def admin_add_job(job: AdminJobIn, _: CurrentUser = Depends(require_admin)):
    row = insert_job(job.title, job.company or "", job.skills or "", job.description)
    return {"job": row}


@router.delete("/jobs/{job_id}", status_code=204)
async def admin_delete_job(job_id: str, _: CurrentUser = Depends(require_admin)):
    delete_job(job_id)


@router.get("/career-notes")
async def admin_list_notes(_: CurrentUser = Depends(require_admin)):
    return {"notes": list_career_notes()}


@router.post("/career-notes", status_code=201)
async def admin_add_note(note: AdminCareerNoteIn, _: CurrentUser = Depends(require_admin)):
    chunks = chunk_text(note.content, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="Content produced no chunks.")
    rows = [
        {"filename": note.filename, "chunk_index": i, "content": chunk}
        for i, chunk in enumerate(chunks)
    ]
    insert_career_note_chunks(rows)
    return {"filename": note.filename, "chunks": len(rows)}


@router.delete("/career-notes/{filename}", status_code=204)
async def admin_delete_note(filename: str, _: CurrentUser = Depends(require_admin)):
    delete_career_note(filename)


@router.get("/stats")
async def admin_stats(_: CurrentUser = Depends(require_admin)):
    return {"jobs": jobs_count(), "career_note_chunks": career_notes_count()}
