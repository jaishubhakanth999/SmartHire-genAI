# data/career_notes/

The **knowledge base for the AI Career Mentor**.

Curated career-guidance documents (interview preparation, skill roadmaps,
industry guidance, CV conventions). These are chunked, embedded, and loaded
into Supabase's `career_notes` table (pgvector) by `backend/scripts/seed_data.py`,
so mentor answers are grounded in this corpus rather than the model's own recall.

Five notes are included:

- `resume_basics.txt` — resume writing fundamentals
- `switching_to_data_analyst.txt` — career-change guide
- `software_engineering_career.txt` — SWE career path and interviews
- `machine_learning_career.txt` — ML/AI engineering skills and career path
- `interview_preparation.txt` — behavioural + technical interview prep

Add more `.txt` notes here — role guides, interview-prep tips, skill
roadmaps — then either re-run the seed script:

```bash
cd backend
python -m scripts.seed_data --notes-only
```

or add documents one at a time from the **Admin panel** in the running app
(no CLI needed after initial setup).

This corpus is what makes the mentor a *RAG* system instead of a plain chatbot.
