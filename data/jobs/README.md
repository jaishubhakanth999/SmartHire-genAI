# data/jobs/

Job descriptions that form the **matching corpus**.

`SAMPLE_jobs.csv` in this folder is an 86-row synthetic dataset spanning
tech, data, product, design, sales, marketing, HR, finance and operations
roles, structured the same way as the Naukri/LinkedIn Kaggle dumps referenced
in the project spec (title, company, skills, description columns). It is
large and diverse enough to exercise semantic search meaningfully (86 vectors
in the live FAISS index) and is what the evaluation report in
`reports/answer_quality.md` was generated against.

To swap in the real Kaggle dataset instead: download a Naukri/LinkedIn job
postings CSV, drop it here, and either delete `SAMPLE_jobs.csv` or point
`job_search.build_job_index(csv_path=...)` at the real file, then rebuild.

- One CSV, one row per job (title, company, skills, description columns --
  `src/search/job_search.py` also recognises a few common alternate column
  names used by different Kaggle dumps).
- Loaded by `src/search/job_search.load_job_dataset()`, embedded and indexed
  into FAISS by `src/search/embed.py`, and queried by `search_jobs()`.
- Rebuild the index after replacing the CSV: `python -m src.search.job_search --build`.
