"""CV improvement suggestions, resume rewrite, and match explanation (Module 3)."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, get_current_user
from app.database import get_job, get_resume, insert_cv_suggestion
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


@router.post("/suggestions", response_model=CVActionResponse)
async def cv_suggestions_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    content = suggest_improvements(resume["parsed"], job)
    insert_cv_suggestion(resume["id"], job["id"], "suggestions", content)
    return {"content": content}


@router.post("/rewrite", response_model=CVActionResponse)
async def cv_rewrite_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    content = rewrite_resume_for_job(resume["parsed"], job)
    insert_cv_suggestion(resume["id"], job["id"], "rewrite", content)
    return {"content": content}


@router.post("/explain", response_model=CVActionResponse)
async def cv_explain_endpoint(req: CVActionRequest, user: CurrentUser = Depends(get_current_user)):
    resume, job = _load_resume_and_job(req, user)
    content = explain_match(resume["parsed"], job)
    insert_cv_suggestion(resume["id"], job["id"], "explanation", content)
    return {"content": content}
