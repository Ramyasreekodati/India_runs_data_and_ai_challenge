# 🤖 Redrob AI Ranker

Welcome to **Team Antigravity's** submission for the Intelligent Candidate Discovery & Ranking Challenge. 

This repository contains our custom-built, constraint-aware heuristic ranking engine designed to isolate the top 100 candidates from a massive 100,000 JSONL pool.

## 🏆 Engineering Philosophy
We chose a **Multi-Level Heuristic Funnel with a Streaming Min-Heap** instead of naive Semantic Search. 
* **Why?** Data profiling revealed that 99% of candidates are irrelevant, and there are active "Keyword Stuffers" in the dataset (e.g., Marketing Managers listing "RAG"). Semantic embeddings on 100k candidates would violate the 5-minute CPU constraint and fall for keyword traps. 
* **Result**: Our O(N log K) streaming approach processes 100,000 records, applies continuous behavioral penalties (e.g., for purely consulting backgrounds or low response rates), and outputs deterministic, hallucination-free reasoning in just **~10.5 seconds** with **< 100MB of RAM**.

## 🚀 Reproducing the Submission CSV

### Prerequisites
* Python 3.11+
* No external API keys required. All execution runs locally on CPU.

### Execution Command
To reproduce our final `team_antigravity.csv` from the raw candidate data in under 15 seconds, run the following command from the root of this repository:

```bash
# Windows (PowerShell)
$env:PYTHONPATH="." ; python src/app/main.py path/to/candidates.jsonl team_antigravity.csv

# Linux / Mac
PYTHONPATH="." python src/app/main.py path/to/candidates.jsonl team_antigravity.csv
```

## 📊 Streamlit Interactive Sandbox
We have built an interactive presentation layer to walk judges through our Data Profiling, Feature Engineering, and final Top 100 results. 

To run the sandbox locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🏗️ Repository Architecture
* `docs/`: Contains our rigorous engineering governance, including the **Engineering Playbook**, **Knowledge Base**, and **Architecture Decision Records (ADRs)**.
* `src/candidate_engine/`: Parses JSON records into structured feature objects and flags traps.
* `src/job_engine/`: Encodes the specific constraints and negative signals from the JD.
* `src/feature_engineering/`: Extracts continuous penalty/boost scores based on behavior, market popularity (log-scaled), and technical skills.
* `src/retrieval/`: The blazing-fast Min-Heap streaming funnel.
* `src/ranking/`: Fuses sub-scores into a monotonic final score (Max 1.0).
* `src/reasoning/`: The deterministic, non-generative explainability engine.
* `app.py`: The Streamlit presentation layer.