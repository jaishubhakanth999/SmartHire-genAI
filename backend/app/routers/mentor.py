"""AI Career Mentor chat endpoint with persistent per-user conversation history."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import CurrentUser, get_current_user
from app.database import (
    create_chat_session,
    delete_chat_session,
    get_chat_session,
    insert_chat_message,
    list_chat_messages,
    list_chat_sessions,
)
from app.schemas import MentorChatRequest, MentorChatResponse
from app.services.guardrails import redact_pii
from app.services.mentor import ask_mentor

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


def _history_pairs(messages: list[dict]) -> list[dict]:
    pairs: list[dict] = []
    pending_question = None
    for message in messages:
        if message["role"] == "user":
            pending_question = message["content"]
        elif message["role"] == "assistant" and pending_question is not None:
            pairs.append({"question": pending_question, "answer": message["content"]})
            pending_question = None
    return pairs


@router.get("/sessions")
async def sessions(user: CurrentUser = Depends(get_current_user)):
    return {"sessions": list_chat_sessions(user.id)}


@router.get("/sessions/{session_id}")
async def session_detail(session_id: str, user: CurrentUser = Depends(get_current_user)):
    session = get_chat_session(session_id, user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return {
        "id": session["id"],
        "title": session.get("title"),
        "created_at": session["created_at"],
        "messages": list_chat_messages(session_id),
    }


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_session(session_id: str, user: CurrentUser = Depends(get_current_user)):
    if not delete_chat_session(session_id, user.id):
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return None


@router.post("/chat", response_model=MentorChatResponse)
async def chat(req: MentorChatRequest, user: CurrentUser = Depends(get_current_user)):
    if req.session_id:
        session = get_chat_session(req.session_id, user.id)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        title = " ".join(req.message.strip().split())[:60] or "New career chat"
        session = create_chat_session(user.id, title)

    session_id = session["id"]
    prior_messages = list_chat_messages(session_id)
    history = _history_pairs(prior_messages)
    insert_chat_message(session_id, "user", redact_pii(req.message))

    try:
        result = ask_mentor(req.message, history=history)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Mentor service failed: {exc}") from exc

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
