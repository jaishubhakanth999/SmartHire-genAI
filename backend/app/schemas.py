"""Pydantic request/response models shared across routers."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class ResumeListResponse(BaseModel):
    resumes: List[ResumeOut]


class CVActionRequest(BaseModel):
    resume_id: str
    job_id: str


class CVActionResponse(BaseModel):
    content: str


class CVHistoryItem(BaseModel):
    id: str
    resume_id: str
    job_id: Optional[str] = None
    kind: str
    content: str
    created_at: str


class MentorChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None


class MentorChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[str] = []
    grounded: bool = True
    blocked: bool = False


class MentorSessionOut(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: str


class MentorSessionDetail(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: str
    messages: List[dict]


class AdminJobIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=160)
    company: Optional[str] = Field(default="", max_length=160)
    skills: Optional[str] = Field(default="", max_length=1000)
    description: str = Field(min_length=10, max_length=10000)


class AdminJobOut(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    skills: Optional[str] = None
    description: str


class AdminCareerNoteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=20, max_length=50000)


class AdminCareerNoteChunkOut(BaseModel):
    id: str
    filename: str
    chunk_index: int
    content: str
