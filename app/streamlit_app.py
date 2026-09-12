"""
Streamlit user interface.

Responsibility: presentation only. Upload a CV, show the parsed profile,
ranked job matches and CV suggestions, and provide the mentor chat panel.

This layer contains NO business logic -- every action calls into src/.
Keeping it thin is what makes the pipeline testable independent of the UI.
"""

import tempfile
from pathlib import Path

import streamlit as st

from src.config import load_config
from src.generate.cv_suggestions import explain_match, suggest_improvements
from src.mentor.rag_chain import ask_mentor, build_mentor_index
from src.parsing.resume_parser import parse_resume, to_search_text
from src.safety import guardrails
from src.search.embed import index_exists
from src.search.job_search import build_job_index, search_jobs

st.set_page_config(page_title="SmartHire GenAI", layout="wide")


def _index_status():
    config = load_config()
    jobs_ready = index_exists(config.vectorstore_dir / "jobs")
    mentor_ready = index_exists(config.vectorstore_dir / "career_notes")
    return jobs_ready, mentor_ready


def _sidebar():
    st.sidebar.title("SmartHire GenAI")
    st.sidebar.caption("Resume Matching & AI Career Mentor")

    jobs_ready, mentor_ready = _index_status()
    st.sidebar.markdown("**Index status**")
    st.sidebar.write(f"Job index: {'✅ ready' if jobs_ready else '⬜ not built'}")
    st.sidebar.write(f"Mentor index: {'✅ ready' if mentor_ready else '⬜ not built'}")

    if st.sidebar.button("Build / rebuild job index"):
        with st.spinner("Embedding job dataset..."):
            try:
                build_job_index()
                st.sidebar.success("Job index built.")
            except Exception as exc:
                st.sidebar.error(str(exc))

    if st.sidebar.button("Build / rebuild mentor index"):
        with st.spinner("Embedding career notes..."):
            try:
                build_mentor_index(force_rebuild=True)
                st.sidebar.success("Mentor index built.")
            except Exception as exc:
                st.sidebar.error(str(exc))


def _resume_tab():
    st.header("Resume matching")
    uploaded = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    if not uploaded:
        st.info("Upload a resume to see your parsed profile and matching jobs.")
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / uploaded.name
        tmp_path.write_bytes(uploaded.getvalue())

        with st.spinner("Parsing resume with the LLM..."):
            try:
                resume = parse_resume(tmp_path)
            except Exception as exc:
                st.error(f"Couldn't parse this resume: {exc}")
                return

    st.session_state["resume"] = resume

    st.subheader("Parsed profile")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {resume.get('name') or '-'}")
        st.write(f"**Email:** {resume.get('email') or '-'}")
        st.write(f"**Phone:** {resume.get('phone') or '-'}")
        st.write(f"**Target role:** {resume.get('target_role') or '-'}")
    with col2:
        st.write("**Skills:**", ", ".join(resume.get("skills", [])) or "-")

    with st.expander("Experience / Education (raw parsed JSON)"):
        st.json({k: v for k, v in resume.items() if k not in ("raw_text",)})

    st.subheader("Matched jobs")
    if not index_exists(load_config().vectorstore_dir / "jobs"):
        st.warning("Build the job index from the sidebar first.")
        return

    with st.spinner("Searching job index..."):
        try:
            matches = search_jobs(to_search_text(resume))
        except Exception as exc:
            st.error(str(exc))
            return

    for i, job in enumerate(matches):
        with st.expander(f"{i + 1}. {job['title']} @ {job['company']} -- score {job['score']}"):
            st.write(job["description"])
            if st.button("Explain this match", key=f"explain_{i}"):
                with st.spinner("Asking the LLM..."):
                    st.write(explain_match(resume, job))
            if st.button("Suggest CV improvements for this job", key=f"suggest_{i}"):
                with st.spinner("Asking the LLM..."):
                    st.write(suggest_improvements(resume, job))


def _mentor_tab():
    st.header("AI Career Mentor")
    st.caption("Answers are grounded in data/career_notes/ -- ask career questions, not general trivia.")

    if not index_exists(load_config().vectorstore_dir / "career_notes"):
        st.warning("Build the mentor index from the sidebar first.")
        return

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for turn in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn.get("sources"):
                st.caption("Sources: " + ", ".join(turn["sources"]))
            if not turn.get("grounded", True):
                st.caption("⚠️ This answer may not be fully grounded in the retrieved documents.")

    question = st.chat_input("Ask a career question...")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.spinner("Thinking..."):
            result = ask_mentor(question, history=st.session_state["chat_history"])
        with st.chat_message("assistant"):
            st.write(result["answer"])
            if result["sources"]:
                st.caption("Sources: " + ", ".join(result["sources"]))
        st.session_state["chat_history"].append(
            {
                "question": guardrails.redact_pii(question),
                "answer": result["answer"],
                "sources": result["sources"],
                "grounded": result["grounded"],
            }
        )


def main():
    """Streamlit entry point."""
    _sidebar()
    st.title("SmartHire GenAI")
    tab1, tab2 = st.tabs(["Resume matching", "Career Mentor"])
    with tab1:
        _resume_tab()
    with tab2:
        _mentor_tab()


if __name__ == "__main__":
    main()
