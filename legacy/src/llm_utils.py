"""
Shared LLM call helper.

Responsibility: the Sarvam API occasionally returns an empty completion for
an otherwise valid request (observed during evaluation -- see
reports/answer_quality.md's method notes). Retrying once or twice resolves
it every time seen in practice. Centralised here so every call site (resume
parsing, CV suggestions, the mentor) gets the same retry behaviour instead of
each module reimplementing it.
"""

import time
from typing import List

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.5


def invoke_with_retry(llm, messages, max_attempts: int = MAX_ATTEMPTS):
    """
    Call llm.invoke(messages) and retry if the response content is empty.

    Raises the last exception if every attempt errors, or returns the final
    (possibly still empty) response if every attempt succeeds but stays empty
    -- callers already validate output via src.safety.guardrails.check_output.
    """
    last_response = None
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = llm.invoke(messages)
        except Exception as exc:  # transient network/API errors
            last_exception = exc
            if attempt < max_attempts:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise
        content = getattr(response, "content", None)
        if content and content.strip():
            return response
        last_response = response
        if attempt < max_attempts:
            time.sleep(RETRY_DELAY_SECONDS)
    return last_response
