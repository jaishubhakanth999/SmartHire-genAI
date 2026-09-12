# SmartHire GenAI — Resume Matching & AI Career Mentor

University capstone project. Two capabilities in one application:

1. **Resume Matching** — parse a candidate CV with an LLM into structured JSON,
   embed it, and retrieve the most relevant jobs from a FAISS vector index.
2. **AI Career Mentor** — a retrieval-augmented (RAG) chat assistant that answers
   career questions grounded in a curated set of career notes.

> **Status: all modules implemented and wired together.**
> The job dataset (`data/jobs/SAMPLE_jobs.csv`) and one resume
> (`data/resumes/SAMPLE_resume.txt`) are small **synthetic placeholders** so
> the pipeline can be run end-to-end right now. Before final submission,
> replace the job CSV with the real Kaggle Naukri/LinkedIn dataset (spec
> section 5) and add real/anonymised sample resumes.

---

## Technology stack

| Concern | Choice |
|---|---|
| Language | Python 3.10+ |
| Generation | Sarvam AI (`langchain-sarvam`, model `sarvam-105b`) |
| Embeddings | Local, free — `sentence-transformers/all-MiniLM-L6-v2` via `langchain-huggingface` |
| Vector store | FAISS (local, persisted to `vectorstore/`) |
| Orchestration | LangChain |
| UI | Streamlit |
| Document parsing | PyPDF (`.pdf`), python-docx (`.docx`) |
| Job dataset | pandas (CSV) |
| Version control | Git / GitHub |
| Deployment | Streamlit Community Cloud |

No technologies outside this list are used. Embeddings run locally so the
only paid API calls are to Sarvam AI, for resume parsing, CV suggestions,
match explanations and mentor answers.

---

## Repository layout

```
smarthire-genai/
├── README.md              project overview, setup, run instructions
├── requirements.txt       pinned Python dependencies
├── .env.example           template for secrets/config (never commit .env)
├── .gitignore             keeps secrets, indexes and caches out of Git
├── data/                  all source corpora (inputs, not code)
│   ├── jobs/              job dataset (SAMPLE_jobs.csv is a placeholder)
│   ├── resumes/           sample/test CVs in PDF, DOCX or TXT form
│   └── career_notes/      knowledge base documents for the mentor RAG chain
├── vectorstore/           persisted FAISS index + metadata (build artefact)
├── notebooks/             exploration and prototyping, not production code
├── src/                   the library — importable, testable, UI-agnostic
├── app/                   Streamlit presentation layer only
└── reports/               written deliverables for assessment
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in LLM_API_KEY and LLM_MODEL
```

## Build the two FAISS indexes

```bash
# Job index (from data/jobs/*.csv)
python -m src.search.job_search --build

# Mentor index (from data/career_notes/) builds automatically the first time
# the mentor is asked a question, or rebuild explicitly:
python -c "from src.mentor.rag_chain import build_mentor_index; build_mentor_index(force_rebuild=True)"
```

## Run the app

```bash
streamlit run app/streamlit_app.py
```

## Run the evaluation harness

```bash
python -m src.evaluate
```

Writes real, freshly-computed results into `reports/answer_quality.md` from
the test cases in `reports/eval_test_set.json` (edit that file to add your
own resumes and mentor questions).

---

## Build order

1. ✅ Project architecture and folder structure
2. ✅ Config + document loading and resume parsing (LLM structured output)
3. ✅ Embeddings + FAISS index build
4. ✅ Job search / matching
5. ✅ CV improvement suggestions
6. ✅ Mentor RAG chain
7. ✅ Guardrails
8. ✅ Evaluation harness (run it to get real numbers — none are pre-filled)
9. ✅ Streamlit UI, wiring every module above together
10. ⬜ Swap in the real Kaggle job dataset, GitHub push, deployment, final report
