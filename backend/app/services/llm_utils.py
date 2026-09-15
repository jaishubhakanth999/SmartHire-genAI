"""
Shared LLM call helper.

Responsibility: call the configured Sarvam model with a small retry policy,
normalize LangChain response content into plain text, and fail clearly when
the provider returns no usable completion.
"""

import time
from typing import Any

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.5


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part.strip()).strip()
    return str(content).strip()


def response_text(response: Any) -> str:
    return _content_to_text(getattr(response, "content", None))


def invoke_with_retry(llm, messages, max_attempts: int = MAX_ATTEMPTS):
    """Invoke the model, retrying transient failures and empty completions."""
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = llm.invoke(messages)
            if response_text(response):
                return response
        except Exception as exc:
            last_exception = exc
            if attempt >= max_attempts:
                raise

        if attempt < max_attempts:
            time.sleep(RETRY_DELAY_SECONDS)

    if last_exception is not None:
        raise last_exception
    raise RuntimeError("AI provider returned an empty response after retries.")
