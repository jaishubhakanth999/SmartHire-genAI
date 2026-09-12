"""AI Career Mentor chat endpoint (Module 4), with per-session conversation memory."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import CurrentUser, get_current_user
from app.database import (
    create_chat_session,
    get_chat_session,
    insert_chat_message,
    list_chat_messages,
)
from app.schemas import MentorChatRequest, MentorChatResponse
from app.services.guardrails import redact_pii
from app.services.mentor import ask_mentor

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


def _history_pairs(messages: list[dict]) -> list[dict]:
    """Turn a flat list of {role, content} rows into {question, answer} pairs for the prompt."""
    pairs = []
    pending_question = None
    for m in messages:
        if m["role"] == "user":
            pending_question = m["content"]
        elif m["role"] == "assistant" and pending_question is not None:
            pairs.append({"question": pending_question, "answer": m["content"]})
            pending_question = None
    return pairs


@router.post("/chat", response_model=MentorChatResponse)
async def chat(req: MentorChatRequest, user: CurrentUser = Depends(get_current_user)):
    if req.session_id:
        session = get_chat_session(req.session_id, user.id)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        title = req.message[:60]
        session = create_chat_session(user.id, title)

    session_id = session["id"]
    prior_messages = list_chat_messages(session_id)
    history = _history_pairs(prior_messages)

    insert_chat_message(session_id, "user", redact_pii(req.message))

    result = ask_mentor(req.message, history=history)

    insert_chat_message(
        session_id,
        "assistant",
        result["answer"],
        sources=result.get("sources", []),
        grounded=result.get("grounded", True),
        blocked=result.get("blocked", False),
    )

    return {
        "session_id": session_id,
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "grounded": result.get("grounded", True),
        "blocked": result.get("blocked", False),
    }
