# data/career_notes/

The **knowledge base for the AI Career Mentor**.

Curated career-guidance documents (interview preparation, skill roadmaps,
industry guidance, CV conventions). These are chunked, embedded and retrieved
by `src/mentor/rag_chain.py` so mentor answers are grounded in this corpus
rather than the model's own recall.

Two starter notes are included (`resume_basics.txt`,
`switching_to_data_analyst.txt`) so the mentor index has something real to
retrieve from immediately. Add more `.txt`/`.pdf`/`.docx` notes here --
role guides, interview-prep tips, skill roadmaps -- then rebuild the mentor
index (sidebar button in the Streamlit app, or
`src.mentor.rag_chain.build_mentor_index(force_rebuild=True)`).

This folder is what makes the mentor a *RAG* system instead of a plain chatbot.
