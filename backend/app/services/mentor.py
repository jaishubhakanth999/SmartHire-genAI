"""Direct AI Career Mentor service without embeddings or RAG."""

from typing import Any, Dict, List, Optional

from langchain_sarvam import ChatSarvam

from app.config import settings
from app.services import guardrails
from app.services.llm_utils import invoke_with_retry, response_text

_llm: Optional[ChatSarvam] = None


def get_llm() -> ChatSarvam:
    global _llm
    if _llm is None:
        settings.require_llm()
        _llm = ChatSarvam(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            temperature=0.2,
            max_tokens=4096,
            reasoning_effort="low",
        )
    return _llm


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
        return {
            "answer": f"I can't help with that: {reason}",
            "sources": [],
            "blocked": True,
            "grounded": True,
        }

    messages = [
        (
            "system",
            "You are SmartHire's AI Career Mentor. Give practical, clear and encouraging career "
            "guidance for students and job seekers. You can answer questions about careers, skills, "
            "learning roadmaps, interviews, job search, resumes, and professional development. "
            "Use your general knowledge and the conversation history. Do not claim to have searched "
            "the internet or accessed private documents. Do not invent facts about the user. If a "
            "question is unrelated to career or professional development, politely redirect it to "
            "a career-focused topic. Keep responses useful and reasonably concise."
        ),
        (
            "human",
            f"CONVERSATION HISTORY:\n{_format_history(history)}\n\nUSER QUESTION:\n{question}",
        ),
    ]

    try:
        response = invoke_with_retry(get_llm(), messages)
        answer = response_text(response)
    except Exception as exc:
        raise RuntimeError(f"Sarvam AI request failed: {exc}") from exc

    if not answer:
        raise RuntimeError("Sarvam AI returned an empty response.")

    is_valid_output, reason = guardrails.check_output(answer)
    if not is_valid_output:
        return {
            "answer": f"I can't share that response: {reason}",
            "sources": [],
            "blocked": True,
            "grounded": True,
        }

    return {
        "answer": answer,
        "sources": [],
        "grounded": True,
        "blocked": False,
    }
