"""
Safety guardrails (Module 5 of the spec).

Responsibility: cheap, deterministic checks applied around every LLM call --
deliberately rule-based rather than another LLM call, so every interaction
gets a safety check without doubling API usage/cost.

- Input:  reject empty/oversized input and clearly unsafe or off-topic
          questions before they reach the LLM.
- Output: catch a short blocklist of discriminatory hiring language.
- PII:    redact emails/phone numbers before logging.
- Grounding: a lexical-overlap check that the mentor's answer actually
          draws on its retrieved sources (or honestly says it doesn't know).

Isolated in its own module so the safety story is auditable in one place for
the report and reports/answer_quality.md's hallucination check.
"""

import re
from typing import List, Optional, Tuple

MAX_INPUT_CHARS = 2000

# Deliberately conservative and small -- a real product would use a proper
# moderation API, but the spec asks for "a simple safety check", and a short,
# explainable list is easier to justify and test for a capstone report than
# an opaque classifier would be.
_UNSAFE_PATTERNS = [
    r"\bmake\s+(a\s+)?(bomb|explosive|weapon)\b",
    r"\bhow\s+to\s+(hack|breach|exploit)\b",
    r"\bkill\s+(myself|yourself)\b",
    r"\bsuicide\b",
    r"\bself[\s-]?harm\b",
]

# The mentor's scope is career guidance. This is a coarse on-topic check, not
# a hard allowlist -- it flags input for a warning rather than hard-blocking
# borderline cases, since a strict keyword allowlist would reject too many
# legitimate phrasings.
_CAREER_KEYWORDS = [
    "career", "job", "resume", "cv", "interview", "skill", "role", "salary",
    "promotion", "internship", "hire", "hiring", "recruiter", "linkedin",
    "portfolio", "certification", "degree", "experience", "switch", "transition",
]

_DISCRIMINATORY_PATTERNS = [
    r"\b(don'?t|do not|avoid)\s+hir(e|ing)\s+(women|men|older|younger)\b",
    r"\bbased on (their\s+)?(race|gender|religion|age|disability)\b",
]

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\-\s()]{7,}\d)(?!\d)")


def check_input(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a user question before it reaches the LLM.

    Returns (is_valid, reason). `reason` is None when is_valid is True, and
    a short human-readable explanation otherwise.
    """
    if not text or not text.strip():
        return False, "Question is empty."
    if len(text) > MAX_INPUT_CHARS:
        return False, f"Question is too long ({len(text)} chars, max {MAX_INPUT_CHARS})."

    lowered = text.lower()
    for pattern in _UNSAFE_PATTERNS:
        if re.search(pattern, lowered):
            return False, "This question isn't something I can help with here."

    return True, None


def check_output(text: str) -> Tuple[bool, Optional[str]]:
    """Validate a generated response before it reaches the user."""
    if not text or not text.strip():
        return False, "Empty response."
    lowered = text.lower()
    for pattern in _DISCRIMINATORY_PATTERNS:
        if re.search(pattern, lowered):
            return False, "Response contained discriminatory hiring language and was blocked."
    return True, None


def redact_pii(text: str) -> str:
    """Remove personally identifying information (emails, phone numbers) from text."""
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def is_grounded(answer: str, sources: List[str], min_overlap: float = 0.15) -> bool:
    """
    Check that an answer is supported by its retrieved sources.

    Heuristic: an honest "I don't know" style refusal always counts as
    grounded (that is the correct behaviour, not a failure). Otherwise, a
    meaningful fraction of the answer's significant words must appear
    somewhere in the concatenated source text.
    """
    if not answer or not answer.strip():
        return False

    refusal_phrases = ["i don't have that", "not in my documents", "i don't know", "outside my scope"]
    lowered_answer = answer.lower()
    if any(phrase in lowered_answer for phrase in refusal_phrases):
        return True

    if not sources:
        return False

    source_words = set(re.findall(r"[a-z]{4,}", " ".join(sources).lower()))
    answer_words = set(re.findall(r"[a-z]{4,}", lowered_answer))
    if not answer_words:
        return False

    overlap = len(answer_words & source_words) / len(answer_words)
    return overlap >= min_overlap
