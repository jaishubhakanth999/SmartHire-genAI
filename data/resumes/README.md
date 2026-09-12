# data/resumes/

Sample candidate CVs used for development, demos and evaluation.

`SAMPLE_resume.txt` is a synthetic test fixture (not a real person) added so
`src/search/job_search.py` can be smoke-tested without needing a real PDF/DOCX
yet. Add a couple of real (anonymised) or synthetic PDF/DOCX resumes here to
exercise `src/parsing/resume_parser.py`'s LLM-based parsing.

- `.pdf` files are read with PyPDF; `.docx` files with python-docx.
- Parsed by `src/parsing/resume_parser.py` into structured fields.
- **Use anonymised or synthetic resumes only.** Real CVs are gitignored.
