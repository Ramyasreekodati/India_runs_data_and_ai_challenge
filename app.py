import streamlit as st
import pandas as pd
import json
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.app.main import run_pipeline

st.set_page_config(page_title="Intelligent Candidate Ranking", layout="wide", page_icon="🤖")

st.title("🤖 Redrob AI: Intelligent Candidate Discovery")
st.markdown("### A Professional AI Engineering Approach to Candidate Ranking")

st.sidebar.header("⚙️ Configuration")
st.sidebar.markdown("Adjust the ranking weights. The system is completely dynamic.")
tech_weight = st.sidebar.slider("Technical Weight", 0.0, 1.0, 0.45)
exp_weight = st.sidebar.slider("Experience Weight", 0.0, 1.0, 0.25)
beh_weight = st.sidebar.slider("Behavior Weight", 0.0, 1.0, 0.20)
mkt_weight = st.sidebar.slider("Market Weight", 0.0, 1.0, 0.10)

config = {
    "tech_weight": tech_weight,
    "exp_weight": exp_weight,
    "beh_weight": beh_weight,
    "mkt_weight": mkt_weight
}

st.sidebar.markdown("---")
st.sidebar.header("📁 Data Input")
st.sidebar.markdown("Upload a candidate JSONL file to run the pipeline.")
uploaded_file = st.sidebar.file_uploader("Upload candidates.jsonl", type=["jsonl", "json"])

default_local_path = "../India_runs_data_and_ai_challenge/candidates.jsonl"
if uploaded_file is not None:
    with open("temp_upload.jsonl", "wb") as f:
        f.write(uploaded_file.getbuffer())
    input_path = "temp_upload.jsonl"
else:
    input_path = default_local_path

if 'results' not in st.session_state:
    st.session_state.results = None

if st.sidebar.button("🚀 Run Ranking Pipeline", type="primary"):
    if not os.path.exists(input_path):
        st.sidebar.error(f"Cannot find dataset at {input_path}")
    else:
        progress_bar = st.progress(0, text="Loading Pipeline...")
        time.sleep(0.5)
        
        progress_bar.progress(30, text="Streaming Candidates (Retrieval Funnel)...")
        results = run_pipeline(input_path, "team_antigravity.csv", config)
        
        progress_bar.progress(70, text="Executing Multi-Level Fusion Ranking...")
        time.sleep(0.5)
        
        progress_bar.progress(90, text="Generating Zero-Hallucination Reasoning...")
        time.sleep(0.5)
        
        progress_bar.progress(100, text="Done!")
        st.session_state.results = results
        st.toast("Pipeline execution completed successfully!", icon="✅")

if st.session_state.results is None:
    st.info("👈 Click **Run Ranking Pipeline** in the sidebar to execute the pipeline and view live results.")
else:
    results = st.session_state.results
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Requirements", "Dataset", "Features", "Ranking", "Evaluation", "Results (Decision Explorer)"])
    
    with tab1:
        st.header("Job Analysis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Mandatory Skills", results.job_analysis.mandatory_skills_count)
        c2.metric("Preferred Skills", results.job_analysis.preferred_skills_count)
        c3.metric("Disqualifying Personas", results.job_analysis.disqualifying_personas_count)

    with tab2:
        st.header("Dataset Analysis")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Processed", results.dataset_analysis.total_processed)
        c2.metric("AI Titles Detected", results.dataset_analysis.ai_titles_detected)
        c3.metric("Keyword Stuffers", results.dataset_analysis.keyword_stuffers_flagged)
        c4.metric("Missing Values", results.dataset_analysis.missing_values_rate)
        
        st.subheader("Retrieval Funnel")
        funnel_data = pd.DataFrame({
            "Stage": ["Total", "Heuristic Pass", "Retrieved (Min-Heap)", "Final Ranked"],
            "Count": [
                results.retrieval_funnel.total_processed,
                results.retrieval_funnel.heuristic_pass,
                results.retrieval_funnel.retrieved_top_k,
                results.retrieval_funnel.final_ranked
            ]
        })
        st.bar_chart(funnel_data.set_index("Stage"))

    with tab3:
        st.header("Feature Summary")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Technical", results.feature_summary.technical)
        c2.metric("Behavior", results.feature_summary.behavior)
        c3.metric("Experience", results.feature_summary.experience)
        c4.metric("Risk", results.feature_summary.risk)
        c5.metric("Market", results.feature_summary.market)

    with tab4:
        st.header("Ranking Engine")
        st.markdown("Current Custom Fusion Weights:")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Technical", f"{config['tech_weight']:.2f}")
        c2.metric("Experience", f"{config['exp_weight']:.2f}")
        c3.metric("Behavior", f"{config['beh_weight']:.2f}")
        c4.metric("Market", f"{config['mkt_weight']:.2f}")
        
    with tab5:
        st.header("Execution Evaluation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Runtime", f"{results.profiling.runtime_seconds:.2f}s")
        c2.metric("Peak Memory", f"{results.profiling.peak_memory_mb:.1f} MB")
        c3.metric("Format Validator", "✅ Passed" if results.profiling.validator_passed else "❌ Failed")

    with tab6:
        st.header("Decision Explorer")
        st.markdown("Select a candidate to view the exact breakdown of their rank.")
        
        df = results.top_candidates
        
        # Display the main table
        st.dataframe(df[["candidate_id", "rank", "score", "reasoning"]], use_container_width=True)
        
        # Decision Explorer
        st.subheader("🔍 Deep Dive: Candidate Breakdown")
        candidate_list = df["candidate_id"].tolist()
        selected_cand = st.selectbox("Select Candidate to Explore", candidate_list)
        
        cand_data = df[df["candidate_id"] == selected_cand].iloc[0]
        st.markdown(f"### {cand_data['candidate_id']} (Rank {cand_data['rank']})")
        st.info(cand_data["reasoning"])
        
        st.markdown("#### Mathematical Evidence")
        raw_breakdown = cand_data["raw_breakdown"]
        bc1, bc2, bc3, bc4 = st.columns(4)
        bc1.metric("Technical Score", f"{raw_breakdown.get('Technical_Score', 0):.2f}")
        bc2.metric("Experience Score", f"{raw_breakdown.get('Experience_Score', 0):.2f}")
        bc3.metric("Behavior Score", f"{raw_breakdown.get('Behavior_Score', 0):.2f}")
        bc4.metric("Market Score", f"{raw_breakdown.get('Market_Score', 0):.2f}")
        
        csv_data = df[["candidate_id", "rank", "score", "reasoning"]].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Final CSV",
            data=csv_data,
            file_name="team_antigravity.csv",
            mime="text/csv",
            type="primary"
        )
