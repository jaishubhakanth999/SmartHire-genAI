"""Pydantic request/response models shared across routers."""

from typing import List, Optional

from pydantic import BaseModel


class JobMatchOut(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    skills: Optional[str] = None
    description: str
    similarity: float


class ResumeOut(BaseModel):
    id: str
    filename: str
    parsed: dict
    created_at: str


class ResumeUploadResponse(BaseModel):
    resume: ResumeOut
    matches: List[JobMatchOut]


class CVActionRequest(BaseModel):
    resume_id: str
    job_id: str


class CVActionResponse(BaseModel):
    content: str


class MentorChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class MentorChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[str] = []
    grounded: bool = True
    blocked: bool = False


class MentorHistoryMessage(BaseModel):
    role: str
    content: str
    sources: List[str] = []
    grounded: Optional[bool] = None
    blocked: Optional[bool] = None
    created_at: str


class AdminJobIn(BaseModel):
    title: str
    company: Optional[str] = ""
    skills: Optional[str] = ""
    description: str


class AdminJobOut(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    skills: Optional[str] = None
    description: str


class AdminCareerNoteIn(BaseModel):
    filename: str
    content: str


class AdminCareerNoteChunkOut(BaseModel):
    id: str
    filename: str
    chunk_index: int
    content: str
