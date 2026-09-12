# data/jobs/

Job descriptions that form the **matching corpus**.

`SAMPLE_jobs.csv` in this folder is a small (10-row) synthetic dataset added
only so the pipeline can be built and smoke-tested end to end right now.
**It is not the required dataset.** Before final submission, download the
real Naukri/LinkedIn job postings dataset from Kaggle (see the project
spec, section 5), drop the CSV here, and either delete `SAMPLE_jobs.csv` or
point `job_search.build_job_index(csv_path=...)` at the real file.

- One CSV, one row per job (title, company, skills, description columns --
  `src/search/job_search.py` also recognises a few common alternate column
  names used by different Kaggle dumps).
- Loaded by `src/search/job_search.load_job_dataset()`, embedded and indexed
  into FAISS by `src/search/embed.py`, and queried by `search_jobs()`.
- Rebuild the index after replacing the CSV: `python -m src.search.job_search --build`.
