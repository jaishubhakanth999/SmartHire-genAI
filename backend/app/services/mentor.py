"""
AI Career Mentor -- retrieval-augmented generation.

Responsibility: embed the question, retrieve relevant chunks from the career_notes table via pgvector, assemble the RAG prompt, run guardrails, call the LLM, and return an answer with its source documents so every claim is traceable. Conversation history is passed in by the caller for multi-turn memory.
"""

from typing import Any, Dict, List, Optional

from langchain_sarvam import ChatSarvam

from app.config import settings
from app.database import match_career_notes
from app.services import guardrails
from app.services.embeddings import embed_text
from app.services.llm_utils import invoke_with_retry
from app.services.prompts import MENTOR_RAG_PROMPT

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
    lines = []
    for turn in history:
        lines.append(f"User: {turn.get('question', '')}")
        lines.append(f"Mentor: {turn.get('answer', '')}")
    return "\n".join(lines)


def ask_mentor(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    is_valid, reason = guardrails.check_input(question)
    if not is_valid:
        return {"answer": f"I can't help with that: {reason}", "sources": [], "blocked": True, "grounded": True}

    query_embedding = embed_text(question)
    docs = match_career_notes(query_embedding, settings.top_k)
    context = "\n\n".join(f"[{d.get('filename', 'unknown')}] {d.get('content', '')}" for d in docs)

    messages = MENTOR_RAG_PROMPT.format_messages(
        context=context or "(no relevant documents found)",
        history=_format_history(history),
        question=question,
    )
    answer = invoke_with_retry(get_llm(), messages).content

    is_valid_output, out_reason = guardrails.check_output(answer)
    if not is_valid_output:
        return {"answer": f"I can't share that response: {out_reason}", "sources": [], "blocked": True, "grounded": True}

    source_texts = [d.get("content", "") for d in docs]
    grounded = guardrails.is_grounded(answer, source_texts)
    sources = sorted({d.get("filename", "unknown") for d in docs})

    return {"answer": answer, "sources": sources, "blocked": False, "grounded": grounded}
