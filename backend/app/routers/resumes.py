"""Resume upload, parsing, and job matching endpoint (Modules 1 + 2)."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import CurrentUser, get_current_user
from app.database import insert_resume
from app.schemas import ResumeUploadResponse
from app.services.job_search import search_jobs
from app.services.resume_parser import parse_resume_upload, to_search_text

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10MB).")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    try:
        result = parse_resume_upload(file.filename, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    parsed = result["parsed"]
    resume_row = insert_resume(user.id, file.filename, result["raw_text"], parsed)

    try:
        matches = search_jobs(to_search_text(parsed))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Job search failed: {exc}") from exc

    return {
        "resume": {
            "id": resume_row["id"],
            "filename": resume_row["filename"],
            "parsed": parsed,
            "created_at": resume_row["created_at"],
        },
        "matches": matches,
    }
