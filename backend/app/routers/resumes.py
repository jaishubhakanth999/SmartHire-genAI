"""Resume upload, history, deletion, parsing, and job matching."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import CurrentUser, get_current_user
from app.database import delete_resume, get_resume, insert_resume, list_resumes
from app.schemas import ResumeListResponse, ResumeOut, ResumeUploadResponse
from app.services.job_search import search_jobs
from app.services.resume_parser import parse_resume_upload, to_search_text

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}


def _validate_file(filename: str, content_type: str | None) -> None:
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Please upload a PDF or DOCX resume.")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=422, detail="The uploaded file type is not supported.")


@router.get("", response_model=ResumeListResponse)
async def list_my_resumes(user: CurrentUser = Depends(get_current_user)):
    return {"resumes": list_resumes(user.id)}


@router.get("/{resume_id}/matches")
async def resume_matches(resume_id: str, user: CurrentUser = Depends(get_current_user)):
    resume = get_resume(resume_id, user.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    try:
        matches = search_jobs(to_search_text(resume["parsed"]))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Job search failed: {exc}") from exc
    return {"resume": {"id": resume["id"], "filename": resume["filename"], "parsed": resume["parsed"], "created_at": resume["created_at"]}, "matches": matches}


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resume(resume_id: str, user: CurrentUser = Depends(get_current_user)):
    if not delete_resume(resume_id, user.id):
        raise HTTPException(status_code=404, detail="Resume not found.")
    return None


@router.post("", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    _validate_file(file.filename, file.content_type)

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded resume is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10MB).")

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
