# Embedding Model Comparison

Stretch goal (spec section 11): compare two embedding models and report
which gives better job matches. Both models are evaluated against the same
job corpus and the same test cases in `reports\eval_test_set.json`.

| Model | Dimensions | Build time (s) | Avg query time (s) | Hit rate | Avg rank of hits |
|---|---|---|---|---|---|
| sentence-transformers/all-MiniLM-L6-v2 | 384 | 1.02 | 0.0163 | 8/8 | 1.0 |
| sentence-transformers/all-mpnet-base-v2 | 768 | 4.93 | 0.0814 | 8/8 | 1.12 |

## Per-query detail

### sentence-transformers/all-MiniLM-L6-v2

| Query | Hit | Rank |
|---|---|---|
| Data-analyst-shaped resume | True | 1 |
| ML-engineer-shaped resume | True | 1 |
| Frontend-developer-shaped resume | True | 1 |
| DevOps-shaped resume | True | 1 |
| Data-scientist-shaped resume | True | 1 |
| Product-manager-shaped resume | True | 1 |
| QA-engineer-shaped resume | True | 1 |
| HR-recruiter-shaped resume | True | 1 |

### sentence-transformers/all-mpnet-base-v2

| Query | Hit | Rank |
|---|---|---|
| Data-analyst-shaped resume | True | 2 |
| ML-engineer-shaped resume | True | 1 |
| Frontend-developer-shaped resume | True | 1 |
| DevOps-shaped resume | True | 1 |
| Data-scientist-shaped resume | True | 1 |
| Product-manager-shaped resume | True | 1 |
| QA-engineer-shaped resume | True | 1 |
| HR-recruiter-shaped resume | True | 1 |

## Conclusion

`all-MiniLM-L6-v2` (384-dim) is the project default: it builds and queries faster and, on this job corpus and test set, matches or beats the larger `all-mpnet-base-v2` (768-dim) on hit rate. The larger model's extra dimensionality did not translate into materially better retrieval for this corpus size, so the smaller, faster model was kept as the production default in `src/config.py` (`DEFAULT_EMBEDDING_MODEL`) -- see the table above for the actual numbers behind that call.
