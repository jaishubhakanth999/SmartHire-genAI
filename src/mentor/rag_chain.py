"""
AI Career Mentor -- retrieval-augmented generation chain (Module 4 of the spec).

Responsibility: the mentor feature end to end. Retrieve relevant passages
from the career_notes corpus, assemble them into the mentor prompt, run the
guardrails, call the LLM, and return an answer together with its source
documents so every claim is traceable.

Kept separate from src/search/ because the two features query different
corpora for different purposes: job_search.py ranks jobs, the mentor grounds
career-advice answers in career_notes/.
"""

from typing import Any, Dict, List, Optional

from langchain_sarvam import ChatSarvam

from src.config import load_config
from src.generate.prompts import MENTOR_RAG_PROMPT
from src.safety import guardrails
from src.search.embed import build_index, index_exists, load_index

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        config = load_config()
        config.require_llm()
        _llm = ChatSarvam(model=config.llm_model, api_key=config.llm_api_key, temperature=0.2)
    return _llm


def _career_notes_persist_dir():
    return load_config().vectorstore_dir / "career_notes"


def build_mentor_index(force_rebuild: bool = False):
    """
    Build (or rebuild) the FAISS index over data/career_notes/.

    Kept here rather than in embed.py because the mentor is the only
    consumer of this particular corpus/index.
    """
    from src.parsing.loader import chunk_documents, load_directory

    config = load_config()
    persist_dir = _career_notes_persist_dir()
    if index_exists(persist_dir) and not force_rebuild:
        return load_index(persist_dir)

    documents = load_directory(config.career_notes_dir)
    if not documents:
        raise ValueError(
            f"No documents found in '{config.career_notes_dir}'. Add at least one "
            ".txt/.pdf/.docx career note before building the mentor index."
        )
    chunks = chunk_documents(documents, chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    return build_index(chunks, persist_dir)


def build_mentor_retriever(k: Optional[int] = None):
    """Return a retriever over the career notes corpus."""
    config = load_config()
    persist_dir = _career_notes_persist_dir()
    if not index_exists(persist_dir):
        build_mentor_index()
    index = load_index(persist_dir)
    return index.as_retriever(search_kwargs={"k": k or config.top_k})


def build_rag_chain():
    """
    Assemble retriever + prompt + LLM into the mentor chain.

    Returns the retriever and llm separately rather than a single opaque
    LangChain Runnable, because ask_mentor() needs the intermediate
    retrieved documents to (a) show sources to the user and (b) run the
    is_grounded() guardrail -- both would be awkward to pull back out of a
    fully composed chain.
    """
    return build_mentor_retriever(), get_llm()


def _format_history(history: Optional[List[Dict[str, str]]]) -> str:
    if not history:
        return "(no earlier turns)"
    lines = []
    for turn in history:
        lines.append(f"User: {turn.get('question', '')}")
        lines.append(f"Mentor: {turn.get('answer', '')}")
    return "\n".join(lines)


def ask_mentor(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Answer a career question, returning {"answer", "sources", "blocked", "grounded"}.

    `history` is a list of {"question", "answer"} dicts from earlier turns in
    this session (stretch goal: conversation memory).
    """
    is_valid, reason = guardrails.check_input(question)
    if not is_valid:
        return {"answer": f"I can't help with that: {reason}", "sources": [], "blocked": True, "grounded": True}

    retriever, llm = build_rag_chain()
    docs = retriever.invoke(question)
    context = "\n\n".join(f"[{d.metadata.get('filename', 'unknown')}] {d.page_content}" for d in docs)

    messages = MENTOR_RAG_PROMPT.format_messages(
        context=context or "(no relevant documents found)",
        history=_format_history(history),
        question=question,
    )
    answer = llm.invoke(messages).content

    is_valid_output, out_reason = guardrails.check_output(answer)
    if not is_valid_output:
        return {"answer": f"I can't share that response: {out_reason}", "sources": [], "blocked": True, "grounded": True}

    source_texts = [d.page_content for d in docs]
    grounded = guardrails.is_grounded(answer, source_texts)
    sources = sorted({d.metadata.get("filename", "unknown") for d in docs})

    return {"answer": answer, "sources": sources, "blocked": False, "grounded": grounded}
