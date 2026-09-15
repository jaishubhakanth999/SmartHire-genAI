"""CV improvement suggestions, rewrite, explanation, and saved history."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, get_current_user
from app.database import get_job, get_resume, insert_cv_suggestion, list_cv_suggestions
from app.schemas import CVActionRequest, CVActionResponse
from app.services.cv_suggestions import explain_match, rewrite_resume_for_job, suggest_improvements

router = APIRouter(prefix="/api/cv", tags=["cv"])


def _load_resume_and_job(req: CVActionRequest, user: CurrentUser):
    resume = get_resume(req.resume_id, user.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    job = get_job(req.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return resume, job


def _ai_failure(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=502,
        detail=f"AI service failed: {exc}",
    )


@router.get("/history/{resume_id}")
async def cv_history(resume_id: str, user: CurrentUser = Depends(get_current_user)):
    if get_resume(resume_id, user.id) is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"items": list_cv_suggestions(resume_id, user.id)}


@router.post("/suggestions", response_model=CVActionResponse)
async def cv_suggestions_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    try:
        content = suggest_improvements(resume["parsed"], job)
        if not content or not content.strip():
            raise RuntimeError("AI returned an empty response.")
        insert_cv_suggestion(resume["id"], job["id"], "suggestions", content)
        return {"content": content}
    except HTTPException:
        raise
    except Exception as exc:
        raise _ai_failure(exc) from exc


@router.post("/rewrite", response_model=CVActionResponse)
async def cv_rewrite_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    try:
        content = rewrite_resume_for_job(resume["parsed"], job)
        if not content or not content.strip():
            raise RuntimeError("AI returned an empty response.")
        insert_cv_suggestion(resume["id"], job["id"], "rewrite", content)
        return {"content": content}
    except HTTPException:
        raise
    except Exception as exc:
        raise _ai_failure(exc) from exc


@router.post("/explain", response_model=CVActionResponse)
async def cv_explain_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    try:
        content = explain_match(resume["parsed"], job)
        if not content or not content.strip():
            raise RuntimeError("AI returned an empty response.")
        insert_cv_suggestion(resume["id"], job["id"], "explanation", content)
        return {"content": content}
    except HTTPException:
        raise
    except Exception as exc:
        raise _ai_failure(exc) from exc
