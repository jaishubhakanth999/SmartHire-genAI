# SmartHire GenAI — Final Report

**Resume Matching & AI Career Mentor**
Capstone Project · Generative AI

---

## 1. Introduction

Job seekers face two related but distinct problems: finding roles that actually
match their background (beyond keyword search on job boards), and getting
trustworthy, specific guidance on how to close the gap between their current
profile and a target role. SmartHire GenAI addresses both in one portal, built
entirely from the generative-AI techniques covered in the course: LLM
structured output, embeddings, a FAISS vector database, retrieval-augmented
generation, LangChain orchestration, guardrails, and Streamlit deployment.

**Scope.** Per the project specification, live scraping of LinkedIn/Naukri is
out of scope (Terms of Service); instead the system embeds a static job corpus
and searches it semantically — the same technique a production system would
use against a licensed or self-collected dataset.

## 2. Requirements traced to the specification

| Spec requirement | Where it is implemented |
|---|---|
| Resume parser → structured JSON | `src/parsing/resume_parser.py` (Pydantic-validated `ResumeProfile`) |
| Document loading & chunking | `src/parsing/loader.py` |
| Semantic job search via FAISS | `src/search/embed.py`, `src/search/job_search.py` |
| CV improvement generator | `src/generate/cv_suggestions.py`, prompts in `src/generate/prompts.py` |
| AI Career Mentor (RAG) | `src/mentor/rag_chain.py` |
| Guardrails | `src/safety/guardrails.py` |
| Streamlit portal + deploy | `app/streamlit_app.py` |
| Evaluation (retrieval, answer quality, prompt comparison, hallucination) | `src/evaluate.py`, `reports/answer_quality.md` |
| Stretch: conversation memory | `ask_mentor(question, history=...)` |
| Stretch: cite sources | `ask_mentor()` returns `sources`; shown in the UI |
| Stretch: rewrite resume for a job | `src/generate/cv_suggestions.rewrite_resume_for_job()` |
| Stretch: compare embedding models | `src/embedding_comparison.py`, `reports/embedding_model_comparison.md` |

Every module in spec section 3 (Modules 1–6) and every stretch goal in
section 11 is implemented.

## 3. System architecture

```
Resume upload (PDF / DOCX)
        │
        ▼
Document loader + chunking (src/parsing/loader.py)
        │
        ▼
LLM structured parser ──► clean JSON profile (src/parsing/resume_parser.py)
        │
        ├──► embed profile ──► FAISS search ──► top-N matching jobs
        │       (src/search/embed.py, job_search.py — 86-job corpus)
        │
        ├──► CV improvement prompt ──► suggestions + rewritten summary
        │       (src/generate/cv_suggestions.py)
        │
        └──► AI Career Mentor: RAG over job corpus + career notes
                (src/mentor/rag_chain.py — 5-document knowledge base)
                        │
                  guardrails check (src/safety/guardrails.py)
        │
        ▼
Streamlit portal (app/streamlit_app.py) ──► admin/user auth ──► GitHub + deploy
```

Each module is UI-agnostic and independently testable — `app/streamlit_app.py`
contains no business logic, only presentation, so every capability can also be
exercised from a notebook or a script (see `notebooks/`).

## 4. Technology choices

| Concern | Choice | Why |
|---|---|---|
| LLM | Sarvam AI (`sarvam-105b` via `langchain-sarvam`) | Course-approved provider; native LangChain integration for structured output and chat |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local) | Free, no API cost/latency for the high-volume embedding step; validated against a larger model (section 7) |
| Vector store | FAISS | Specified in the brief; fast, local, no external service dependency |
| Orchestration | LangChain | Prompt templates, structured output, retriever/LLM composition |
| UI | Streamlit | Specified in the brief; fast to build a multi-tab, session-stateful app |
| Auth | Custom session-state login (no external library) | Two fixed demo accounts (admin/user) were sufficient for the assignment scope; avoided pulling in a heavier auth dependency |

## 5. Implementation notes

**Resume parsing.** A single LLM call with `with_structured_output(ResumeProfile)`
returns the whole profile (name, contact, skills, experience, education,
target role) in one shot rather than one call per field — cheaper and
simpler, and Pydantic validation rejects anything that doesn't fit the schema
before it is used downstream. A retry wrapper (`_PARSE_MAX_ATTEMPTS = 3`) was
added after evaluation surfaced occasional empty/invalid completions from the
API (section 7).

**Semantic job search.** The job CSV is loaded tolerantly — `job_search.py`
tries several likely column names (`title`/`job_title`/`Job Title`, etc.) so
the same code works against different Kaggle Naukri/LinkedIn dump schemas
without modification. Each job becomes one FAISS-indexed document; a resume's
flattened profile text is embedded and compared with cosine similarity via
`similarity_search_with_score`.

**CV suggestions and resume rewrite.** Both are grounded strictly in the
parsed profile's existing facts — the prompts explicitly forbid inventing
employers, dates, or skills. `rewrite_resume_for_job()` (stretch goal)
produces a tailored summary/skills/experience block, using only what's
already in the candidate's profile.

**AI Career Mentor.** Retrieves from a 5-document, 16-chunk career-notes
index, formats retrieved passages with their source filename into the
prompt, and returns both the answer and the list of source filenames so
every claim is traceable (stretch goal: citations). Conversation history is
passed as prior Q/A pairs into the prompt (stretch goal: memory).

**Guardrails.** Deliberately rule-based rather than a second LLM call for
every message (`src/safety/guardrails.py`): input length/emptiness and a
small unsafe-pattern list are checked before the LLM call; output is checked
for a short discriminatory-language pattern list after; PII is redacted from
chat history; and a lexical-overlap heuristic (`is_grounded()`) checks that
the mentor's answer actually draws on retrieved text, treating an honest "I
don't know" as correctly grounded rather than a failure.

## 6. Safety and guardrails

Guardrails run on every mentor turn: `check_input()` before the LLM call,
`check_output()` after. Section 7 documents a real before/after prompt
change that closed a scope-adherence gap that guardrails' regex-based
approach deliberately does not attempt to close (a keyword allowlist for
"on-topic" is too brittle — see the comment in `guardrails.py`); that gap
had to be closed in the mentor's system prompt instead, which is the right
layer for it.

## 7. Evaluation

Full results: [`reports/answer_quality.md`](answer_quality.md) and
[`reports/embedding_model_comparison.md`](embedding_model_comparison.md),
both generated by actually running the live pipeline (`python -m
src.evaluate` and `python -m src.embedding_comparison`) against the fixed
test set in `reports/eval_test_set.json` — no numbers below are invented.

- **Retrieval relevance:** 8/8 hit rate, all at rank 1, across 8 resume
  profiles spanning distinct job families against the 86-job corpus.
- **Answer quality:** 8/8 grounded rate across 8 mentor questions, including
  two designed to test refusal (a plausible-but-undocumented salary question,
  and a fully off-topic general-knowledge question).
- **Prompt comparison:** a documented before/after (section 5 of
  `answer_quality.md`) shows the current `MENTOR_SYSTEM_PROMPT` correctly
  declining an off-topic question that a looser, unscoped prompt answered
  from the model's own knowledge instead of the retrieved context.
- **Hallucination check:** confirmed on both the "no salary data in corpus"
  case and the off-topic case — the mentor states it doesn't have the
  information rather than inventing an answer.
- **Embedding model comparison (stretch goal):** `all-MiniLM-L6-v2` (384-dim,
  local default) matches `all-mpnet-base-v2` (768-dim) on hit rate at roughly
  a fifth of the build time, justifying the smaller model as the production
  default rather than assuming bigger is better.
- **Reliability finding:** evaluation surfaced a real, intermittent bug — the
  Sarvam API occasionally returns an empty completion. This was fixed with a
  retry helper (`src/llm_utils.py`) rather than a guardrails workaround; see
  section 4 of `answer_quality.md` for the failure-case writeup.

## 8. Deployment

The app runs locally via `streamlit run app/streamlit_app.py` (see the
project README for full setup) and is structured for one-click deployment to
Streamlit Community Cloud: push to GitHub, connect the repository at
share.streamlit.io, point it at `app/streamlit_app.py`, and set `LLM_API_KEY`
/ `LLM_MODEL` as app secrets (never committed — `.env` is gitignored).
Two demo accounts (`admin`/`admin123`, `user`/`user123`) are available
immediately after deploy with no extra setup.

## 9. Limitations and future work

- The job corpus (86 rows) is a larger, more diverse synthetic stand-in for
  the real Kaggle Naukri/LinkedIn dataset referenced in the spec, structured
  identically so a real dataset can be dropped in by replacing one CSV and
  rebuilding the index — no code changes required.
- Guardrails are intentionally lightweight (regex-based) rather than a
  full moderation model, matching the spec's ask for "a simple safety
  check" — a production system would likely add a dedicated moderation API.
- The mentor's grounding check (`is_grounded()`) is a lexical-overlap
  heuristic, not a semantic entailment model; it is a reasonable proxy at
  this scale but could be strengthened with an LLM-as-judge evaluator.
- Authentication is intentionally simple (two fixed demo accounts) for the
  assignment's scope; a production deployment would use a real identity
  provider and per-user data isolation.

## 10. Conclusion

SmartHire GenAI implements all six required modules and all four stretch
goals from the project specification, backed by a real, reproducible
evaluation rather than a one-off demo: 8/8 retrieval hit rate, 8/8 mentor
grounding rate, a documented prompt improvement with before/after evidence,
a confirmed hallucination/scope-refusal check, and a head-to-head embedding
model comparison. The system is deployable as-is to Streamlit Community
Cloud and swaps in a real job dataset with a single file replacement.

## 11. References

- Project specification: *SmartHire GenAI — Resume Matching & AI Career
  Mentor* (capstone brief, GenAI course)
- Sarvam AI API docs: https://docs.sarvam.ai
- LangChain documentation: https://python.langchain.com
- FAISS: https://github.com/facebookresearch/faiss
- Sentence-Transformers: https://www.sbert.net
- Streamlit documentation: https://docs.streamlit.io
