"""
LLM-generated CV improvement suggestions (Module 3 of the spec).

Responsibility: given a parsed resume and a target job, call the LLM with the
templates in prompts.py to produce concrete, actionable advice -- gaps to
close, wording to strengthen, a rewritten summary.

This is the generation half of the matching feature; job_search.py is the
retrieval half.
"""

import json

from langchain_sarvam import ChatSarvam

from src.config import load_config
from src.generate.prompts import CV_SUGGESTION_PROMPT, MATCH_EXPLANATION_PROMPT, RESUME_REWRITE_PROMPT
from src.llm_utils import invoke_with_retry

_llm = None


def get_llm():
    """Return the configured Sarvam AI chat model for text generation."""
    global _llm
    if _llm is None:
        config = load_config()
        config.require_llm()
        _llm = ChatSarvam(model=config.llm_model, api_key=config.llm_api_key, temperature=0.3)
    return _llm


def _resume_json(resume: dict) -> str:
    # Drop the large raw_text field -- the LLM only needs the structured fields.
    slim = {k: v for k, v in resume.items() if k not in ("raw_text", "source_path")}
    return json.dumps(slim, default=str)


def suggest_improvements(resume: dict, job: dict) -> str:
    """Generate improvement suggestions for a resume against one job."""
    messages = CV_SUGGESTION_PROMPT.format_messages(
        resume_json=_resume_json(resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content


def explain_match(resume: dict, job: dict) -> str:
    """Generate a plain-language explanation of why a job was matched."""
    messages = MATCH_EXPLANATION_PROMPT.format_messages(
        resume_json=_resume_json(resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content


def rewrite_resume_for_job(resume: dict, job: dict) -> str:
    """
    Stretch goal: 'rewrite my resume for this job'.

    Returns a tailored summary/skills/experience rewrite grounded strictly in
    facts already present in `resume` -- never invents new experience.
    """
    messages = RESUME_REWRITE_PROMPT.format_messages(
        resume_json=_resume_json(resume),
        job_title=job.get("title", ""),
        job_description=job.get("description", ""),
    )
    return invoke_with_retry(get_llm(), messages).content
