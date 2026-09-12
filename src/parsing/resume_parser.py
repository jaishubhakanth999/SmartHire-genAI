"""
Resume-specific parsing.

Responsibility: turn the raw text of a CV into a clean, structured profile --
name, contact info, skills, experience, education, target role -- using the
LLM's structured-output mode (Module 1 of the spec), then validate the
result with Pydantic before anything downstream trusts it.

Design note -- this differs slightly from the original placeholder:
the placeholder had one function per field (extract_skills, extract_experience,
...), each implying a separate pass over the raw text. The project spec asks
for a single LLM call that returns the whole JSON profile at once ("send it
to the LLM with a strict prompt, get back clean JSON... validate the JSON
before using it") -- that is both simpler and cheaper (one API call instead
of four). So parse_resume() does the one LLM call, and the extract_* helpers
below just read fields off the already-parsed, already-validated profile
instead of hitting the LLM again.
"""

from typing import List, Optional

from langchain_sarvam import ChatSarvam
from pydantic import BaseModel, Field, ValidationError

from src.config import load_config
from src.generate.prompts import RESUME_PARSE_PROMPT
from src.parsing.loader import load_file


class Experience(BaseModel):
    title: str = Field(description="Job title held.")
    company: str = Field(description="Employer name.")
    start_date: Optional[str] = Field(default=None, description="e.g. 'Jan 2022' or 'unknown'.")
    end_date: Optional[str] = Field(default=None, description="e.g. 'Present' or 'unknown'.")
    description: Optional[str] = Field(default=None, description="One or two lines on responsibilities/impact.")


class Education(BaseModel):
    degree: str = Field(description="Degree or qualification name.")
    institution: str = Field(description="School / university name.")
    year: Optional[str] = Field(default=None, description="Graduation year, if stated.")


class ResumeProfile(BaseModel):
    """The structured JSON profile the LLM must return for a CV."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    target_role: Optional[str] = Field(
        default=None, description="The role the candidate appears to be targeting, if inferable."
    )
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)


_llm = None  # lazy singleton so importing this module never requires an API key


def get_llm():
    """Return a Sarvam AI chat model configured to emit ResumeProfile JSON."""
    global _llm
    if _llm is None:
        config = load_config()
        config.require_llm()
        _llm = ChatSarvam(
            model=config.llm_model,
            api_key=config.llm_api_key,
            temperature=0,
        )
    return _llm


def parse_resume(path) -> dict:
    """
    Load a CV file and return a structured, validated resume profile (dict).

    Raises:
        ValueError: if the file can't be read, or the LLM's output fails
            Pydantic validation even after the structured-output constraint
            (this should be rare, but we never pass unvalidated JSON downstream).
    """
    raw_text = load_file(path)
    structured_llm = get_llm().with_structured_output(ResumeProfile)
    try:
        result = structured_llm.invoke(RESUME_PARSE_PROMPT.format(resume_text=raw_text))
    except Exception as exc:  # network / API errors
        raise ValueError(f"Resume parsing LLM call failed: {exc}") from exc

    if isinstance(result, ResumeProfile):
        profile = result
    else:
        # Some LangChain versions return a dict for with_structured_output.
        try:
            profile = ResumeProfile.model_validate(result)
        except ValidationError as exc:
            raise ValueError(f"LLM returned JSON that failed validation: {exc}") from exc

    resume = profile.model_dump()
    resume["source_path"] = str(path)
    resume["raw_text"] = raw_text
    return resume


def extract_contact_info(resume: dict) -> dict:
    """Pull name, email and phone from an already-parsed resume."""
    return {"name": resume.get("name"), "email": resume.get("email"), "phone": resume.get("phone")}


def extract_skills(resume: dict) -> List[str]:
    """Return the skills list from an already-parsed resume."""
    return resume.get("skills", [])


def extract_experience(resume: dict) -> list:
    """Return the experience entries from an already-parsed resume."""
    return resume.get("experience", [])


def extract_education(resume: dict) -> list:
    """Return the education entries from an already-parsed resume."""
    return resume.get("education", [])


def to_search_text(resume: dict) -> str:
    """Flatten a structured resume into the single string used for job matching."""
    parts = [resume.get("target_role") or "", ", ".join(resume.get("skills", []))]
    for exp in resume.get("experience", []):
        parts.append(f"{exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description') or ''}")
    for edu in resume.get("education", []):
        parts.append(f"{edu.get('degree', '')} - {edu.get('institution', '')}")
    return "\n".join(p for p in parts if p.strip())


if __name__ == "__main__":
    # Quick manual smoke test (requires LLM_API_KEY / LLM_MODEL in .env):
    #   python -m src.parsing.resume_parser data/resumes/sample.pdf
    import json
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.parsing.resume_parser <path-to-resume>")
    parsed = parse_resume(sys.argv[1])
    parsed.pop("raw_text", None)
    print(json.dumps(parsed, indent=2, default=str))
