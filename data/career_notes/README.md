# data/career_notes/

The **knowledge base for the AI Career Mentor**.

Curated career-guidance documents (interview preparation, skill roadmaps,
industry guidance, CV conventions). These are chunked, embedded and retrieved
by `src/mentor/rag_chain.py` so mentor answers are grounded in this corpus
rather than the model's own recall.

Five notes are included, covering the areas the mentor is evaluated on in
`reports/eval_test_set.json`:

- `resume_basics.txt` -- resume writing fundamentals
- `switching_to_data_analyst.txt` -- career-change guide
- `software_engineering_career.txt` -- SWE career path and interviews
- `machine_learning_career.txt` -- ML/AI engineering skills and career path
- `interview_preparation.txt` -- behavioural + technical interview prep

Add more `.txt`/`.pdf`/`.docx` notes here -- role guides, interview-prep tips,
skill roadmaps -- then rebuild the mentor index (sidebar button in the
Streamlit app, or `src.mentor.rag_chain.build_mentor_index(force_rebuild=True)`).

This folder is what makes the mentor a *RAG* system instead of a plain chatbot.
