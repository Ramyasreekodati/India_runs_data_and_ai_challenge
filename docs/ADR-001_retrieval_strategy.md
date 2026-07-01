# ADR-001: Retrieval Strategy (Phase 2 Output)

## Status
Proposed (Pending Approval)

## Context & Evidence
In **Phase 2**, we profiled the 100,000 candidates dataset and found the following empirical evidence:
- **Dataset Size**: ~465 MB uncompressed.
- **Candidate Distribution**: 99% of candidates hold completely unrelated generic roles (e.g., HR Manager, Accountant, Civil Engineer). Only ~832 candidates hold explicit AI/ML titles.
- **Keyword Stuffers**: We confirmed exactly 395 "Marketing" candidates who injected heavy AI keywords (RAG, Pinecone, LLM) into their skill arrays.
- **Constraints**: 5-minute wall clock, CPU-only, 16GB RAM limit.

## Decision
We will build a **Multi-Level Heuristic Funnel with a Streaming Min-Heap** rather than relying on a pure semantic search / Vector DB (like BM25 or SentenceTransformers) for the initial retrieval pass.

## Rationale (Why this over alternatives)
1. **Alternative 1: Full-Dataset Semantic Search (BM25 or Embeddings)**
   - *Rejected because*: Indexing 465MB of text on a CPU within 5 minutes is dangerously close to the timeout limit. Furthermore, semantic search is highly susceptible to the 395 "Keyword Stuffers" we identified. A BM25 algorithm will happily rank a Marketing Manager with 10 instances of the word "RAG" higher than a Staff Engineer who wrote "Information Retrieval" once.
   
2. **Alternative 2: Generative LLM Filtering**
   - *Rejected because*: Violates the strict "No external API" and "No GPU" rules, and would timeout after processing <100 candidates.

3. **Chosen Architecture: Streaming Heuristic Min-Heap**
   - *Why*: By streaming the `candidates.jsonl` file one line at a time, parsing explicit structural features (e.g., current title, years of experience, recruiter response rate), and computing a fast arithmetic "Heuristic Score", we can filter 100,000 candidates down to a Top 3,000 pool in **O(N log K)** time and **O(K)** space. 
   - *Result*: This guarantees completion in < 15 seconds and uses < 10MB of memory, leaving 4 minutes and 45 seconds to perform rigorous re-ranking on just the Top 3,000.

## Validation
We will implement the streaming parser and min-heap in Phase 3/4. If the execution time exceeds 30 seconds or misses obvious AI engineers (evaluated in Phase 6), this ADR will be revised.
