# SmartHire GenAI — Resume Matching & AI Career Mentor

> **Capstone Project · Generative AI**
> Built with: LLM APIs · Embeddings · FAISS · RAG · LangChain · Streamlit

An end-to-end Generative AI career portal where a candidate uploads a resume and
the system returns:

1. **Parsed profile** — structured JSON extracted from the CV by the LLM
2. **Matched jobs** — semantic search over a job corpus using FAISS + embeddings
3. **CV suggestions** — LLM-generated, actionable improvement advice for each job
4. **AI Career Mentor** — RAG-based chatbot grounded in career notes (LangChain)

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
| Embeddings | Local/free — `sentence-transformers/all-MiniLM-L6-v2` |
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
├── data/
│   ├── jobs/              job dataset (CSV)
│   ├── resumes/           sample resumes for testing
│   └── career_notes/      knowledge base for the mentor RAG chain
├── vectorstore/           persisted FAISS indexes (build artefact)
├── notebooks/             exploration notebooks
├── src/                   importable library — all business logic
│   ├── config.py
│   ├── parsing/           loader.py, resume_parser.py
│   ├── search/            embed.py, job_search.py
│   ├── generate/          prompts.py, cv_suggestions.py
│   ├── mentor/            rag_chain.py
│   ├── safety/            guardrails.py
│   └── evaluate.py
├── app/
│   └── streamlit_app.py   Streamlit UI (presentation only)
└── reports/
    ├── answer_quality.md
    ├── eval_test_set.json
    └── final_report_OUTLINE.md
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
# Job index (reads data/jobs/*.csv)
python -m src.search.job_search --build

# Mentor index (reads data/career_notes/)
python -c "from src.mentor.rag_chain import build_mentor_index; build_mentor_index(force_rebuild=True)"
```

Alternatively, sign in as **admin** in the app and click the sidebar buttons.

## Run the app

```bash
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501 and log in:
- `admin` / `admin123` for the admin view
- `user` / `user123` for the candidate view

## Run the evaluation harness

```bash
python -m src.evaluate
```

Writes results into `reports/answer_quality.md`.

---

## Modules

| Module | File(s) | Technique |
|---|---|---|
| Resume Parser | `src/parsing/resume_parser.py` | Structured output / JSON |
| Document Loading | `src/parsing/loader.py` | Document loading + chunking |
| Semantic Job Search | `src/search/embed.py`, `job_search.py` | Embeddings + FAISS |
| CV Suggestions | `src/generate/cv_suggestions.py` | Prompt engineering + LLM |
| AI Career Mentor | `src/mentor/rag_chain.py` | RAG + LangChain |
| Guardrails | `src/safety/guardrails.py` | Input/output validation |
| Evaluation | `src/evaluate.py` | Quality metrics |
| UI | `app/streamlit_app.py` | Streamlit |

---

## Guardrails

Every user question passes through `src/safety/guardrails.py` before reaching the LLM:
- Empty / oversized inputs are rejected
- Unsafe topic patterns are blocked
- Output is checked for discriminatory language
- PII (email, phone) is redacted before logging to session history
- The mentor's answer is checked for grounding against its retrieved documents

---

## Notes

- API keys live in `.env`, never in code (`LLM_API_KEY` in `.env.example`)
- The job dataset in `data/jobs/SAMPLE_jobs.csv` is a synthetic placeholder.
  For the real dataset, download a Naukri/LinkedIn CSV from Kaggle and replace it.
- The mentor answers from `data/career_notes/` only — it will say "I don't know"
  for questions outside its documents (hallucination guard).
