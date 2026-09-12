"""
Prompt templates.

Responsibility: every prompt used anywhere in the application lives here as a
named, versioned template -- resume parsing, CV suggestions, match
explanations, the mentor's system behaviour and its RAG answer format.

Centralised so prompts can be reviewed and tuned during evaluation (see
src/evaluate.py and reports/answer_quality.md) without touching the modules
that call them.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# ---------------------------------------------------------------------------
# Module 1 -- Resume Parser (structured JSON output)
# ---------------------------------------------------------------------------
RESUME_PARSE_PROMPT = PromptTemplate.from_template(
    """You are extracting a structured profile from a resume for a job-matching system.

Read the resume text below and extract: name, email, phone, the role the
candidate appears to be targeting (or your best inference if not explicit),
their skills, their work experience, and their education.

Rules:
- Only use information present in the text. Do not invent employers, dates,
  or skills that are not there.
- If a field is not present, leave it empty rather than guessing.
- Keep each experience "description" to one or two lines.

Resume text:
---
{resume_text}
---
"""
)

# ---------------------------------------------------------------------------
# Module 3 -- CV Improvement Generator
# ---------------------------------------------------------------------------
CV_SUGGESTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a career coach helping a candidate tailor their CV to a specific "
            "job. Be specific and actionable -- point at concrete gaps and concrete "
            "wording, not generic advice like 'add more detail'. Never invent "
            "experience, employers, or skills the candidate does not have.",
        ),
        (
            "human",
            "CANDIDATE PROFILE (JSON):\n{resume_json}\n\n"
            "TARGET JOB:\nTitle: {job_title}\nDescription: {job_description}\n\n"
            "Give me:\n"
            "1. Missing skills the job wants that the candidate doesn't evidence.\n"
            "2. Two or three weak bullet points from their experience, rewritten to be "
            "stronger (use only facts already in their profile).\n"
            "3. A rewritten 2-3 sentence professional summary targeted at this job.",
        ),
    ]
)

MATCH_EXPLANATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You explain, in two or three plain sentences, why a candidate profile "
            "matches a job posting. Reference specific overlapping skills or "
            "experience. Do not invent overlap that isn't there.",
        ),
        (
            "human",
            "CANDIDATE PROFILE (JSON):\n{resume_json}\n\n"
            "JOB:\nTitle: {job_title}\nDescription: {job_description}\n\n"
            "Why is this a good match?",
        ),
    ]
)

# ---------------------------------------------------------------------------
# Module 4 -- AI Career Mentor (RAG)
# ---------------------------------------------------------------------------
MENTOR_SYSTEM_PROMPT = (
    "You are the SmartHire GenAI Career Mentor. You answer career questions "
    "(career changes, skill roadmaps, interview prep, resume conventions) "
    "using ONLY the retrieved context documents below. "
    "If the answer is not contained in the context, say plainly that you "
    "don't have that in your documents -- do not make something up. "
    "Stay strictly within career-guidance topics; politely decline anything else. "
    "When you use a fact from a document, mention which document it came from."
)

MENTOR_RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", MENTOR_SYSTEM_PROMPT),
        (
            "human",
            "CONTEXT DOCUMENTS:\n{context}\n\n"
            "CONVERSATION SO FAR:\n{history}\n\n"
            "QUESTION:\n{question}",
        ),
    ]
)

_PROMPTS = {
    "resume_parse": RESUME_PARSE_PROMPT,
    "cv_suggestion": CV_SUGGESTION_PROMPT,
    "match_explanation": MATCH_EXPLANATION_PROMPT,
    "mentor_system": MENTOR_SYSTEM_PROMPT,
    "mentor_rag": MENTOR_RAG_PROMPT,
}


def get_prompt(name: str):
    """Look up a prompt template by name."""
    try:
        return _PROMPTS[name]
    except KeyError as exc:
        raise KeyError(f"No prompt named '{name}'. Known prompts: {sorted(_PROMPTS)}") from exc
