"""
SmartHire GenAI backend -- FastAPI entry point.

Run locally:  uvicorn main:app --reload --port 8000
Deploy:       gunicorn -k uvicorn.workers.UvicornWorker main:app  (see render.yaml)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import admin, cv, mentor, resumes

app = FastAPI(title="SmartHire GenAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router)
app.include_router(cv.router)
app.include_router(mentor.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"service": "SmartHire GenAI API", "status": "ok"}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "supabase_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
        "llm_configured": bool(settings.llm_api_key and settings.llm_model),
        "llm_model": settings.llm_model if settings.llm_api_key else None,
    }
