"""
Streamlit portal — SmartHire GenAI.

Includes a login gate with two roles:
  - admin  (password: admin123)  — index management, evaluation, plus all user features
  - user   (password: user123)   — resume upload, job matching, CV suggestions, mentor chat

Credentials are intentionally simple for a capstone demo. In production, use
a secrets manager and bcrypt hashing.
"""

import hashlib
import json
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

st.set_page_config(page_title="SmartHire GenAI", page_icon="🎯", layout="wide")

# ---------------------------------------------------------------------------
# Hard-coded accounts (capstone demo only)
# ---------------------------------------------------------------------------
_ACCOUNTS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "display_name": "Admin",
    },
    "user": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user",
        "display_name": "Career Seeker",
    },
}

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _check_credentials(username: str, password: str) -> bool:
    account = _ACCOUNTS.get(username)
    if not account:
        return False
    return account["password_hash"] == hashlib.sha256(password.encode()).hexdigest()


def _login_page():
    """Render the login form and return True once authenticated."""
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("## 🎯 SmartHire GenAI")
        st.markdown("*Resume Matching & AI Career Mentor*")
        st.divider()

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin or user")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted:
            if _check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = _ACCOUNTS[username]["role"]
                st.session_state["display_name"] = _ACCOUNTS[username]["display_name"]
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption("Demo accounts — admin / admin123  ·  user / user123")


def _logout():
    for key in ["authenticated", "username", "role", "display_name", "resume", "chat_history"]:
        st.session_state.pop(key, None)
    st.rerun()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _index_status():
    config = load_config()
    jobs_ready = index_exists(config.vectorstore_dir / "jobs")
    mentor_ready = index_exists(config.vectorstore_dir / "career_notes")
    return jobs_ready, mentor_ready


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar():
    role = st.session_state.get("role", "user")
    display_name = st.session_state.get("display_name", "")

    with st.sidebar:
        st.markdown(f"### 🎯 SmartHire GenAI")
        st.caption("Resume Matching & AI Career Mentor")
        st.divider()

        st.markdown(f"👤 **{display_name}** (`{role}`)")
        if st.button("Sign out", use_container_width=True):
            _logout()

        st.divider()
        jobs_ready, mentor_ready = _index_status()
        st.markdown("**Index status**")
        st.write(f"Job index: {'✅ ready' if jobs_ready else '⬜ not built'}")
        st.write(f"Mentor index: {'✅ ready' if mentor_ready else '⬜ not built'}")

        if role == "admin":
            st.divider()
            st.markdown("**Admin controls**")
            if st.button("Build / rebuild job index", use_container_width=True):
                with st.spinner("Embedding job dataset…"):
                    try:
                        build_job_index()
                        st.success("Job index built.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

            if st.button("Build / rebuild mentor index", use_container_width=True):
                with st.spinner("Embedding career notes…"):
                    try:
                        build_mentor_index(force_rebuild=True)
                        st.success("Mentor index built.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))


# ---------------------------------------------------------------------------
# Tab: Resume Matching
# ---------------------------------------------------------------------------

def _resume_tab():
    st.header("📄 Resume Matching")
    uploaded = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Your file is processed in memory — nothing is stored on the server.",
    )
    if not uploaded:
        st.info("Upload a resume to see your parsed profile and matching jobs.")
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / uploaded.name
        tmp_path.write_bytes(uploaded.getvalue())

        with st.spinner("Parsing resume with the LLM…"):
            try:
                resume = parse_resume(tmp_path)
            except Exception as exc:
                st.error(f"Couldn't parse this resume: {exc}")
                return

    st.session_state["resume"] = resume

    # ---- Parsed profile ----
    st.subheader("Parsed Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {resume.get('name') or '—'}")
        st.markdown(f"**Email:** {resume.get('email') or '—'}")
        st.markdown(f"**Phone:** {resume.get('phone') or '—'}")
        st.markdown(f"**Target role:** {resume.get('target_role') or '—'}")
    with col2:
        skills = resume.get("skills", [])
        if skills:
            st.markdown("**Skills:**")
            st.write(", ".join(skills))
        else:
            st.markdown("**Skills:** —")

    with st.expander("Full parsed JSON (experience, education…)"):
        st.json({k: v for k, v in resume.items() if k not in ("raw_text",)})

    st.divider()

    # ---- Job matches ----
    st.subheader("Matched Jobs")
    config = load_config()
    if not index_exists(config.vectorstore_dir / "jobs"):
        if st.session_state.get("role") == "admin":
            st.warning("Job index not built yet. Use the sidebar button to build it.")
        else:
            st.warning("The job index is not ready yet. Please ask your admin to build it.")
        return

    with st.spinner("Searching job index…"):
        try:
            matches = search_jobs(to_search_text(resume))
        except Exception as exc:
            st.error(str(exc))
            return

    if not matches:
        st.info("No matching jobs found.")
        return

    for i, job in enumerate(matches):
        score_pct = int(job["score"] * 100)
        with st.expander(
            f"{'🥇' if i == 0 else '🔹'} {i + 1}. **{job['title']}** @ {job['company']}  "
            f"— match {score_pct}%"
        ):
            if job.get("skills"):
                st.markdown(f"**Required skills:** {job['skills']}")
            st.markdown(job["description"])

            c1, c2 = st.columns(2)
            with c1:
                if st.button("💡 Explain this match", key=f"explain_{i}"):
                    with st.spinner("Asking the LLM…"):
                        st.info(explain_match(resume, job))
            with c2:
                if st.button("✏️ CV improvement suggestions", key=f"suggest_{i}"):
                    with st.spinner("Asking the LLM…"):
                        st.success(suggest_improvements(resume, job))


# ---------------------------------------------------------------------------
# Tab: AI Career Mentor
# ---------------------------------------------------------------------------

def _mentor_tab():
    st.header("🤖 AI Career Mentor")
    st.caption(
        "Answers are grounded in **data/career_notes/** — ask career questions, "
        "not general trivia. The mentor will say 'I don't know' if the answer "
        "isn't in its documents."
    )

    config = load_config()
    if not index_exists(config.vectorstore_dir / "career_notes"):
        if st.session_state.get("role") == "admin":
            st.warning("Mentor index not built yet. Use the sidebar button to build it.")
        else:
            st.warning("The mentor index is not ready yet. Please ask your admin to build it.")
        return

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Render conversation history
    for turn in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn.get("sources"):
                st.caption("📚 Sources: " + ", ".join(turn["sources"]))
            if not turn.get("grounded", True):
                st.caption("⚠️ This answer may not be fully grounded in the documents.")

    question = st.chat_input("Ask a career question…")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.spinner("Thinking…"):
            result = ask_mentor(question, history=st.session_state["chat_history"])
        with st.chat_message("assistant"):
            st.write(result["answer"])
            if result.get("sources"):
                st.caption("📚 Sources: " + ", ".join(result["sources"]))
            if not result.get("grounded", True):
                st.caption("⚠️ May not be fully grounded in the documents.")

        st.session_state["chat_history"].append(
            {
                "question": guardrails.redact_pii(question),
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "grounded": result.get("grounded", True),
            }
        )
        if st.button("🗑️ Clear chat", key="clear_chat_bottom"):
            st.session_state["chat_history"] = []
            st.rerun()


# ---------------------------------------------------------------------------
# Tab: Admin Panel (admin only)
# ---------------------------------------------------------------------------

def _admin_tab():
    st.header("⚙️ Admin Panel")
    jobs_ready, mentor_ready = _index_status()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Job Index", "Ready ✅" if jobs_ready else "Not built ⬜")
    with col2:
        st.metric("Mentor Index", "Ready ✅" if mentor_ready else "Not built ⬜")

    st.divider()

    # ---- Evaluation report ----
    st.subheader("📊 Evaluation Report")
    report_path = Path("reports/answer_quality.md")
    if report_path.exists():
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.info(
            "No evaluation report yet. Run `python -m src.evaluate` from the "
            "project root to generate one."
        )

    st.divider()

    # ---- Test set viewer ----
    st.subheader("🧪 Evaluation Test Set")
    test_path = Path("reports/eval_test_set.json")
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)
        st.json(test_data)
    else:
        st.info("No test set found at reports/eval_test_set.json.")

    st.divider()

    # ---- Config snapshot ----
    st.subheader("🔧 Current Config")
    try:
        config = load_config()
        st.json(
            {
                "llm_model": config.llm_model,
                "embedding_model": config.embedding_model,
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "top_k": config.top_k,
                "data_dir": str(config.data_dir),
                "vectorstore_dir": str(config.vectorstore_dir),
            }
        )
    except Exception as exc:
        st.error(str(exc))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    # Gate: show login if not authenticated
    if not st.session_state.get("authenticated"):
        _login_page()
        return

    role = st.session_state.get("role", "user")

    _sidebar()

    st.title("🎯 SmartHire GenAI")
    st.caption("Resume Matching & AI Career Mentor — powered by Sarvam AI")

    if role == "admin":
        tab_resume, tab_mentor, tab_admin = st.tabs(
            ["📄 Resume Matching", "🤖 Career Mentor", "⚙️ Admin Panel"]
        )
        with tab_resume:
            _resume_tab()
        with tab_mentor:
            _mentor_tab()
        with tab_admin:
            _admin_tab()
    else:
        tab_resume, tab_mentor = st.tabs(["📄 Resume Matching", "🤖 Career Mentor"])
        with tab_resume:
            _resume_tab()
        with tab_mentor:
            _mentor_tab()


if __name__ == "__main__":
    main()
