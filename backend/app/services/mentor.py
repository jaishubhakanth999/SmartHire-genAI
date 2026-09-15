"""Direct AI Career Mentor service using Sarvam only."""

from typing import Any, Dict, List, Optional

from app.config import settings
from app.services import guardrails
from app.services.sarvam_client import chat


def _format_history(history: Optional[List[Dict[str, str]]]) -> str:
    if not history:
        return "(no earlier turns)"
    lines: list[str] = []
    for turn in history[-8:]:
        question = str(turn.get("question", "")).strip()
        answer = str(turn.get("answer", "")).strip()
        if question:
            lines.append(f"User: {question}")
        if answer:
            lines.append(f"Mentor: {answer}")
    return "\n".join(lines) or "(no earlier turns)"


def ask_mentor(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    is_valid, reason = guardrails.check_input(question)
    if not is_valid:
        return {"answer": f"I can't help with that: {reason}", "sources": [], "blocked": True, "grounded": True}

    settings.require_llm()
    messages = [
        {
            "role": "system",
            "content": (
                "You are SmartHire's AI Career Mentor. Give practical, clear and encouraging "
                "career guidance for students and job seekers. Answer questions about careers, "
                "skills, learning roadmaps, interviews, job search, resumes, and professional "
                "development. Use general model knowledge and the conversation history. Do not "
                "claim to have searched the internet or accessed private documents. Do not invent "
                "facts about the user. For unrelated topics, politely redirect to career guidance. "
                "Keep answers useful and reasonably concise."
            ),
        },
        {
            "role": "user",
            "content": f"CONVERSATION HISTORY:\n{_format_history(history)}\n\nQUESTION:\n{question}",
        },
    ]

    try:
        answer = chat(messages, max_tokens=2500)
    except Exception as exc:
        raise RuntimeError(f"Sarvam AI mentor request failed: {exc}") from exc

    is_valid_output, reason = guardrails.check_output(answer)
    if not is_valid_output:
        return {"answer": f"I can't share that response: {reason}", "sources": [], "blocked": True, "grounded": True}

    return {"answer": answer, "sources": [], "grounded": True, "blocked": False}
