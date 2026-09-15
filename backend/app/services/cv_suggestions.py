"""
LLM-generated CV improvement suggestions, match explanations, and resume rewrites.

Responsibility: given a parsed resume and a target job, call the LLM with the
templates in prompts.py to produce concrete, actionable output.
"""

import json
from typing import Optional

from langchain_sarvam import ChatSarvam

from app.config import settings
from app.services.llm_utils import invoke_with_retry
from app.services.prompts import CV_SUGGESTION_PROMPT, MATCH_EXPLANATION_PROMPT, RESUME_REWRITE_PROMPT

_llm: Optional[ChatSarvam] = None


def get_llm() -> ChatSarvam:
    global _llm
    if _llm is None:
        settings.require_llm()
        _llm = ChatSarvam(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            temperature=0.3,
            max_tokens=4096,
            reasoning_effort="low",
        )
    return _llm


def _resume_json(parsed: dict) -> str:
    return json.dumps(parsed, default=str)


def suggest_improvements(parsed_resume: dict, job: dict) -> str:
    messages = CV_SUGGESTION_PROMPT.format_messages(
        resume_json=_resume_json(parsed_resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content


def explain_match(parsed_resume: dict, job: dict) -> str:
    messages = MATCH_EXPLANATION_PROMPT.format_messages(
        resume_json=_resume_json(parsed_resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content


def rewrite_resume_for_job(parsed_resume: dict, job: dict) -> str:
    messages = RESUME_REWRITE_PROMPT.format_messages(
        resume_json=_resume_json(parsed_resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content
