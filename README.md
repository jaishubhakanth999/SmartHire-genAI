# SmartHire GenAI — Resume Matching & AI Career Mentor

> **Capstone Project · Generative AI**
> Built with: LLM APIs · Embeddings · FAISS · RAG · LangChain · Streamlit

An end-to-end Generative AI career portal where a candidate uploads a resume and
the system returns:

1. **Parsed profile** — structured JSON extracted from the CV by the LLM
2. **Matched jobs** — semantic search over an 86-job corpus using FAISS + embeddings
3. **CV suggestions** — LLM-generated, actionable improvement advice for each job
4. **Tailored resume rewrite** — a rewritten summary/skills/experience block for a target job
5. **AI Career Mentor** — RAG-based chatbot grounded in 5 career-notes documents (LangChain)

All 6 core modules and all 4 stretch goals from the project spec are implemented
and backed by a real, reproducible evaluation — see
[`reports/final_report.md`](reports/final_report.md).

---

## Demo accounts

| Role  | Username | Password  | Capabilities |
|-------|----------|-----------|--------------|
| Admin | `admin`  | `admin123` | Build indexes, run evaluation, all user features |
| User  | `user`   | `user123`  | Upload resume, match jobs, chat with mentor |

---

## Technology stack

| Concern | Choice |
|---|---|
| Language | Python 3.10+ |
| LLM | Sarvam AI (`langchain-sarvam`, model `sarvam-105b`) |
| Embeddings | Local/free — `sentence-transformers/all-MiniLM-L6-v2` (validated against `all-mpnet-base-v2`, see comparison report) |
| Vector store | FAISS (persisted to `vectorstore/`) |
| Orchestration | LangChain |
| UI | Streamlit |
| Document parsing | PyPDF (`.pdf`), python-docx (`.docx`) |
| Job dataset | pandas (CSV) |
| Deployment | Streamlit Community Cloud |

---

## Repository layout

```
smarthire-genai/
├── README.md
├── requirements.txt
├── .env.example           ← copy to .env and fill in your API key
├── .gitignore
├── .streamlit/config.toml
├── .claude/launch.json     dev-server config
├── data/
│   ├── jobs/              86-row job corpus (CSV)
│   ├── resumes/           sample resume for testing
│   └── career_notes/      5-document knowledge base for the mentor RAG chain
├── vectorstore/           persisted FAISS indexes (build artefact)
├── notebooks/
│   ├── 01_embeddings_explore.ipynb        embedding sanity checks + chunk-size tuning
│   ├── 02_build_faiss.ipynb               build & query the job FAISS index
│   └── 03_rag_prototype.ipynb             mentor RAG chain, grounding, memory
├── src/                   importable library — all business logic
│   ├── config.py
│   ├── llm_utils.py        shared LLM-call retry helper
│   ├── embedding_comparison.py   stretch goal: compare 2 embedding models
│   ├── parsing/           loader.py, resume_parser.py
│   ├── search/            embed.py, job_search.py
│   ├── generate/          prompts.py, cv_suggestions.py
│   ├── mentor/            rag_chain.py
│   ├── safety/            guardrails.py
│   └── evaluate.py
├── app/
│   └── streamlit_app.py   Streamlit UI (admin/user auth + presentation only)
└── reports/
    ├── final_report.md              the written report (all 11 sections)
    ├── answer_quality.md            live evaluation results
    ├── embedding_model_comparison.md
    └── eval_test_set.json           fixed test set for both reports
```

---

## Setup

```bash
# 1. Clone the repo and enter it
git clone https://github.com/jaishubhakanth999/SmartHire-genAI.git
cd SmartHire-genAI

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and set LLM_API_KEY to your Sarvam AI key
```

## Build the FAISS indexes

```bash
# Job index (reads data/jobs/*.csv, 86 rows)
python -m src.search.job_search --build

# Mentor index (reads data/career_notes/, 5 documents)
python -c "from src.mentor.rag_chain import build_mentor_index; build_mentor_index(force_rebuild=True)"
```

Alternatively, sign in as **admin** in the app and click the sidebar buttons.

## Run the app

**Always run from the project root, using the venv's Python** — running from
another directory or with a different Python is the most common cause of
`ModuleNotFoundError: No module named 'src'`:

```bash
# Windows
.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py

# macOS/Linux
.venv/bin/python -m streamlit run app/streamlit_app.py
```

Then open http://localhost:8501 and log in:
- `admin` / `admin123` for the admin view
- `user` / `user123` for the candidate view

`app/streamlit_app.py` also inserts the project root onto `sys.path`
automatically as a safety net, so it works even if Streamlit is launched
from a different working directory.

## Run the evaluation harness

```bash
python -m src.evaluate
```

Writes real, freshly-computed results into `reports/answer_quality.md` from
the test cases in `reports/eval_test_set.json`.

## Run the embedding model comparison (stretch goal)

```bash
python -m src.embedding_comparison
```

Builds a temporary FAISS index with each of two embedding models
(`all-MiniLM-L6-v2` vs `all-mpnet-base-v2`), evaluates both against the same
test set, and writes `reports/embedding_model_comparison.md`.

---

## Modules

| Module | File(s) | Technique |
|---|---|---|
| Resume Parser | `src/parsing/resume_parser.py` | Structured output / JSON |
| Document Loading | `src/parsing/loader.py` | Document loading + chunking |
| Semantic Job Search | `src/search/embed.py`, `job_search.py` | Embeddings + FAISS |
| CV Suggestions + Rewrite | `src/generate/cv_suggestions.py` | Prompt engineering + LLM |
| AI Career Mentor | `src/mentor/rag_chain.py` | RAG + LangChain, conversation memory, citations |
| Guardrails | `src/safety/guardrails.py` | Input/output validation |
| Evaluation | `src/evaluate.py` | Quality metrics |
| Embedding comparison | `src/embedding_comparison.py` | Stretch goal |
| UI | `app/streamlit_app.py` | Streamlit, admin/user auth |

---

## Guardrails

Every user question passes through `src/safety/guardrails.py` before reaching the LLM:
- Empty / oversized inputs are rejected
- Unsafe topic patterns are blocked
- Output is checked for discriminatory language
- PII (email, phone) is redacted before logging to session history
- The mentor's answer is checked for grounding against its retrieved documents
- Off-topic scope enforcement is handled by the mentor's system prompt
  (documented as a before/after prompt comparison in `reports/answer_quality.md`)

---

## Evaluation results (summary)

Full detail in [`reports/answer_quality.md`](reports/answer_quality.md):

- **Retrieval hit rate:** 8/8 (all at rank 1) across 8 distinct resume/job-family pairs
- **Mentor grounded rate:** 8/8, including a hallucination check and an off-topic scope-refusal check
- **Prompt comparison:** documented before/after showing a scoped system prompt correctly declining an off-topic question that an unscoped prompt answered from the model's own knowledge

---

## Notes

- API keys live in `.env`, never in code (`LLM_API_KEY` in `.env.example`)
- `data/jobs/SAMPLE_jobs.csv` is an 86-row synthetic dataset structured like
  the Naukri/LinkedIn Kaggle dumps referenced in the spec. Swap in the real
  dataset by replacing this CSV and rebuilding the index — no code changes needed.
- The mentor answers from `data/career_notes/` only — it will say "I don't know"
  for questions outside its documents (hallucination guard).
