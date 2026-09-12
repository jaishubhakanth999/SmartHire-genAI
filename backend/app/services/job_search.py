"""
Semantic job search.

Responsibility: embed a candidate's flattened profile text and run a
cosine-similarity search against the `jobs` table via the match_jobs()
Postgres function (supabase/migrations/0002_functions.sql). All storage and
indexing lives in Supabase/pgvector -- this module only embeds the query and
shapes the RPC's results.
"""

from typing import Any, Dict, List

from app.config import settings
from app.database import match_jobs
from app.services.embeddings import embed_text


def search_jobs(resume_search_text: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    """
    Return the top-k jobs most similar to a resume's flattened search text.

    Each result is {"id", "title", "company", "skills", "description", "similarity"}.
    """
    query_embedding = embed_text(resume_search_text)
    k = top_k or settings.top_k
    return match_jobs(query_embedding, k)
