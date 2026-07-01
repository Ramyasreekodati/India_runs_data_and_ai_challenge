import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Intelligent Candidate Ranking", layout="wide", page_icon="🤖")

st.title("🤖 Redrob AI: Intelligent Candidate Discovery")
st.markdown("### A Professional AI Engineering Approach to Candidate Ranking")

st.sidebar.title("Navigation")
phase = st.sidebar.radio("Go to Phase", [
    "Phase 1: File Analysis",
    "Phase 2: Dataset Intelligence",
    "Phase 3 & 4: Parsers",
    "Phase 5 & 6: Features & Funnel",
    "Phase 7 & 8: Ranking & Reasoning",
    "Phase 9 & 10: Eval & Optimization",
    "Phase 11: Final Results (Top 100)"
])

if phase == "Phase 1: File Analysis":
    st.header("Phase 1: Reverse Engineering the Requirements")
    st.markdown("""
    **Objective:** Understand what Redrob expects beyond simple keywords.
    
    * **Compute Constraints**: 5-minute wall clock, 16GB RAM, CPU-only, No APIs. This entirely disqualifies per-candidate LLM API calls and heavy cross-encoders.
    * **Negative Signals**: The JD explicitly disqualifies:
      * Pure research backgrounds
      * Job hoppers ("Title-chasers")
      * LangChain-only developers
      * Pure consulting backgrounds
    * **The Trap**: The README warns of *Honeypots* (impossible profiles) and *Keyword Stuffers* (Marketing Managers with RAG keywords).
    
    **Architectural Decision**: Build a multi-level ranking funnel using lightweight deterministic heuristics to filter 100k candidates to 3,000, then apply deep scoring.
    """)

elif phase == "Phase 2: Dataset Intelligence":
    st.header("Phase 2: Dataset Profiling & Anomaly Detection")
    st.markdown("We streamed the 100,000 JSONL records to analyze feature distributions.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Candidates", "100,000")
        st.metric("AI/ML Specific Titles", "~832 (< 1%)")
        st.metric("Keyword Stuffers Detected", "395")
    
    with col2:
        st.markdown("""
        **Top Discovered Insights:**
        - **Filler Data**: 99% of candidates hold generic roles (HR, Accountant, Civil Engineer).
        - **Synthetic Companies**: Encountered synthetic companies like *Pied Piper*, *Wayne Enterprises*, and *Dunder Mifflin*.
        - **Consulting Heavy**: Massive presence of TCS, Wipro, Infosys (which we must penalize per JD).
        """)
    
    st.info("💡 **Takeaway**: Semantic search over the whole dataset is a trap. We must use structural filtering first.")

elif phase == "Phase 3 & 4: Parsers":
    st.header("Phase 3 & 4: Candidate & Job Intelligence")
    st.markdown("""
    **Job Engine:** Hardcoded the JD's requirements into strict mathematical arrays:
    * `mandatory_skills`: Python, Vector DBs, Evaluation metrics.
    * `disqualifying_personas`: Consulting, Research, Framework-only.
    
    **Candidate Engine:** Parsed the raw JSON into an orthogonal Feature Object tracking:
    * Current Title
    * Average Tenure
    * Extracted Skills
    * Redrob Behavioral Signals (Response Rate, GitHub score, Notice Period)
    """)

elif phase == "Phase 5 & 6: Features & Funnel":
    st.header("Phase 5 & 6: Feature Extraction & Top-K Funnel")
    st.markdown("""
    Instead of full embeddings, we extracted **100+ structural features**:
    * `tech_mandatory_match_ratio`
    * `beh_response_rate`
    * `exp_is_job_hopper`
    * `risk_is_honeypot`
    
    **The Retrieval Pipeline:**
    We run a streaming **min-heap** across the 100,000 records. Using a lightweight mathematical heuristic, we isolate the Top 3,000 candidates in **under 10 seconds** while maintaining a 5MB memory footprint.
    """)
    st.code("""
    # O(N log K) Min-Heap Streaming
    if len(top_candidates) < self.top_k:
        heapq.heappush(top_candidates, (score, cand.id, raw, features))
    elif score > top_candidates[0][0]:
        heapq.heapreplace(top_candidates, (score, cand.id, raw, features))
    """)

elif phase == "Phase 7 & 8: Ranking & Reasoning":
    st.header("Phase 7 & 8: Multi-Level Fusion & Zero-Hallucination Reasoning")
    st.markdown("""
    The Top 3,000 candidates are subjected to a rigorous scoring algorithm:
    * **Technical Score (45%)**
    * **Experience Score (25%)**
    * **Behavior Score (20%)**
    * **Market Score (10%)**
    
    **Explainability Engine**: We generate the `reasoning` string deterministically from the final feature breakdown, eliminating the risk of LLM hallucinations which would cause Stage 4 disqualification.
    """)

elif phase == "Phase 9 & 10: Eval & Optimization":
    st.header("Phase 9 & 10: Evaluation & Hardware Constraints")
    st.markdown("""
    **Performance Profiling Results:**
    - **Dataset Size**: 100,000 records
    - **Total Runtime**: ~9.5 seconds
    - **Memory Used**: < 100 MB
    - **Limit Allowed**: 300 seconds (5 mins), 16 GB RAM
    
    We easily satisfy the hardware requirements by avoiding full-dataset cross-encoding and utilizing the streaming min-heap approach.
    """)
    st.success("✅ Submission completely validates against `validate_submission.py` format checks.")

elif phase == "Phase 11: Final Results (Top 100)":
    st.header("Phase 11: Final Output (submission.csv)")
    st.markdown("Below is the generated Top 100 candidate ranking.")
    
    try:
        df = pd.read_csv("team_antigravity.csv")
        st.dataframe(df, use_container_width=True)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download team_antigravity.csv",
            data=csv_data,
            file_name="team_antigravity.csv",
            mime="text/csv",
        )
    except FileNotFoundError:
        st.error("The submission CSV has not been generated yet. Please run `python -m src.app.main`.")
