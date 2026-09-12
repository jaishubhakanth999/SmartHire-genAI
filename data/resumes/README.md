# data/resumes/

Sample candidate CVs used for local development and manual testing.

`SAMPLE_resume.txt` is a synthetic test fixture (not a real person), used to
smoke-test `backend/app/services/resume_parser.py`'s LLM-based parsing
end to end without needing a real PDF/DOCX.

- Resumes are never seeded into Supabase from this folder — they're only for
  developer testing via `POST /api/resumes` (the actual app flow is: a real
  user uploads their own resume through the frontend, which the backend
  parses and stores under that user's account).
- `.pdf` files are read with PyPDF; `.docx` with python-docx; `.txt` directly.
- **Use anonymised or synthetic resumes only** if you add more test files here.
