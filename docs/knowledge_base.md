# Phase 0 & 1: Challenge Knowledge Base

Based on a meticulous analysis of the 5 core competition documents (`readme.txt`, `job_description.txt`, `submission_spec.txt`, `redrob_signals_doc.txt`, and `candidate_schema.json`), here is the evidence-based foundation for our architecture.

## 1. The Constraints (The "Why")
> *Evidence Source: `submission_spec.txt` Section 3*

- **Compute**: ≤ 5 minutes wall-clock, ≤ 16 GB RAM, CPU only, ≤ 5 GB intermediate disk state.
- **Network**: Strictly OFF. No LLM APIs during ranking.
- **Implication**: We cannot use a cross-encoder or an LLM to score all 100,000 candidates. A fast pre-filtering step (heuristics/compact embeddings/BM25) is mathematically required before deep scoring.

## 2. The Evaluation Metrics
> *Evidence Source: `submission_spec.txt` Section 4*

The final score is a weighted composite of IR metrics:
- **0.50 × NDCG@10**: Top 10 must be flawless.
- **0.30 × NDCG@50**: Top 50 must be highly relevant.
- **0.15 × MAP**: General precision across the 100 ranks matters.
- **0.05 × P@10**: Pure binary relevance of the top 10.
- **Tie-breakers**: Higher P@5, then P@10, then earliest submission time. In the CSV, ties must be broken deterministically (e.g., ascending candidate ID).

## 3. The Rejection Traps & Honeypots
> *Evidence Source: `readme.txt` & `submission_spec.txt` Section 7*

- **Keyword Stuffers**: "A candidate who has all the AI keywords... but whose title is 'Marketing Manager' is not a fit."
- **Honeypots (~80 instances)**: Impossible profiles (e.g., "8 years of experience at a company founded 3 years ago" or "'expert' proficiency in 10 skills with 0 years used").
- **Penalty**: Submissions with >10% honeypot rate in the Top 100 are automatically disqualified at Stage 3. Our system *must* have contradiction detection.

## 4. Job Description Explicit Requirements
> *Evidence Source: `job_description.txt`*

### Mandatory Fit
- Production experience with **embeddings-based retrieval systems** (sentence-transformers, OpenAI embeddings, BGE, E5, RAG).
- Production experience with **vector databases** (Pinecone, Weaviate, Qdrant, Milvus, FAISS).
- **Python** programming and ranking evaluation frameworks (**NDCG, MRR, MAP, A/B testing**).
- **Experience Band**: 5–9 years ideal. (4-5 years in applied ML).

### Explicit Disqualifiers (Negative Signals)
- **Pure Research**: Academic labs/research without production deployment.
- **Framework Enthusiasts**: LangChain wrappers without fundamental ML understanding.
- **Pure Consulting**: TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini *only* careers. (Mixed product/consulting is okay).
- **Title Chasers**: Jumping companies every 1.5 years to get Staff/Principal titles.
- **Non-Coding Architects**: Senior engineers who haven't written production code in 18 months.

## 5. Behavioral Signals (The "Availability" Multiplier)
> *Evidence Source: `redrob_signals_doc.txt` & `jd.txt`*

"A perfect-on-paper candidate who hasn't logged in for 6 months and has a 5% recruiter response rate is... not actually available."
- **Key Signals to Weight**: `recruiter_response_rate`, `last_active_date`, `open_to_work_flag`, `notice_period_days` (sub-30 preferred, >30 tolerable).
- **Validation Signals**: `github_activity_score` (validates production engineering).
- **Popularity Signals**: `search_appearance_30d`, `saved_by_recruiters_30d`. (Must use logarithmic scaling to prevent popularity bias).

## 6. The Reasoning Column (Stage 4 Manual Review)
> *Evidence Source: `submission_spec.txt` Section 3*

The reasoning column is strictly evaluated on:
1. **Specific Facts**: Must cite actual YOE, skills, or signal values.
2. **JD Connection**: Relate facts back to the JD.
3. **Honest Concerns**: Must acknowledge gaps (e.g., high notice period).
4. **No Hallucination**: Must not fabricate skills or employers.
5. **Rank Consistency**: Rank 95 shouldn't have glowing praise; Rank 5 shouldn't be overly critical.
- **Conclusion**: We must build a deterministic string builder using the candidate's exact feature dictionary. Generative LLMs are too risky here.

---

### Phase 1 Exit Gate
With the knowledge base built entirely on the provided evidence, we understand exactly *what* we are building for. The next step is **Phase 2: Dataset Intelligence**, where we will analyze the `candidates.jsonl` file to understand the distribution of the 100k candidates and prove/disprove which retrieval methods are viable.
