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
st.sidebar.header("📂 Data Source")

mode = st.sidebar.radio(
    "Choose Data Source",
    [
        "● Demo Dataset (Recommended)", 
        "○ Competition Dataset (100k)", 
        "○ Upload Your Dataset", 
        "○ Upload Candidates + JD"
    ]
)

input_path = None
custom_jd_config = None

if mode == "● Demo Dataset (Recommended)":
    st.sidebar.info("**Dataset**: 50 Candidates\n\n**Purpose**: Quick demonstration\n\n**Expected Runtime**: < 1 second")
    input_path = "demo_candidates.jsonl"
elif mode == "○ Competition Dataset (100k)":
    st.sidebar.warning("**Dataset**: 100,000 Candidates\n\n**Expected Runtime**: 9-15 seconds\n\n*(Must run locally)*")
    input_path = "../India_runs_data_and_ai_challenge/candidates.jsonl"
elif mode == "○ Upload Your Dataset":
    uploaded_file = st.sidebar.file_uploader("Upload Candidates (.json or .jsonl)", type=["jsonl", "json"])
    if uploaded_file is not None:
        with open("temp_upload.jsonl", "wb") as f:
            f.write(uploaded_file.getbuffer())
        input_path = "temp_upload.jsonl"
        st.sidebar.success("Dataset ready.")
elif mode == "○ Upload Candidates + JD":
    uploaded_cand = st.sidebar.file_uploader("1. Upload Candidates (.json or .jsonl)", type=["jsonl", "json"])
    uploaded_jd = st.sidebar.file_uploader("2. Upload Custom JD (.json)", type=["json"])
    if uploaded_cand is not None and uploaded_jd is not None:
        with open("temp_upload.jsonl", "wb") as f:
            f.write(uploaded_cand.getbuffer())
        input_path = "temp_upload.jsonl"
        custom_jd_config = json.loads(uploaded_jd.getvalue().decode("utf-8"))
        st.sidebar.success("Dataset and JD ready.")

if 'results' not in st.session_state:
    st.session_state.results = None

if st.sidebar.button("🚀 Run Ranking Pipeline", type="primary"):
    if input_path is None or not os.path.exists(input_path):
        st.sidebar.error("Data source is missing or not uploaded yet.")
    else:
        progress_bar = st.progress(0, text="Loading Pipeline...")
        time.sleep(0.5)
        
        progress_bar.progress(30, text="Streaming Candidates (Retrieval Funnel)...")
        results = run_pipeline(input_path, "team_antigravity.csv", config, custom_jd_config)
        
        progress_bar.progress(70, text="Executing Multi-Level Fusion Ranking...")
        time.sleep(0.5)
        
        progress_bar.progress(90, text="Generating Zero-Hallucination Reasoning...")
        time.sleep(0.5)
        
        progress_bar.progress(100, text="Done!")
        st.session_state.results = results
        st.toast("Pipeline execution completed successfully!", icon="✅")

if st.session_state.results is None:
    st.info("👈 Choose a **Data Source** and click **Run Ranking Pipeline** to execute the pipeline.")
    st.markdown("""
    ### 🚀 Quick Start
    Don't have a dataset? 
    Select **Demo Dataset (Recommended)** on the left and run the pipeline instantly to explore the system!
    """)
else:
    results = st.session_state.results
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Requirements", "Dataset", "Features", "Ranking", "Evaluation", "Decision Explorer", "Compare Candidates"])
    
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
        
    with tab7:
        st.header("Candidate Comparison")
        st.markdown("Select two candidates to compare their raw scores and see why one outranked the other.")
        
        df = results.top_candidates
        candidate_list = df["candidate_id"].tolist()
        
        c1, c2 = st.columns(2)
        with c1:
            cand_a_id = st.selectbox("Select Candidate A", candidate_list, index=0)
        with c2:
            cand_b_id = st.selectbox("Select Candidate B", candidate_list, index=1 if len(candidate_list) > 1 else 0)
            
        cand_a = df[df["candidate_id"] == cand_a_id].iloc[0]
        cand_b = df[df["candidate_id"] == cand_b_id].iloc[0]
        
        a_breakdown = cand_a["raw_breakdown"]
        b_breakdown = cand_b["raw_breakdown"]
        
        # Calculate Deltas (A - B)
        # If A > B, A is better, so the delta shown on A's side is positive.
        # Streamlit metrics naturally show positive as green.
        
        st.markdown("### Head-to-Head Attributes")
        
        # We will render columns for A and B side-by-side
        colA, colB = st.columns(2)
        
        with colA:
            st.subheader(f"🏆 Candidate A: {cand_a_id}")
            st.markdown(f"**Overall Rank**: {cand_a['rank']} (Score: {cand_a['score']:.4f})")
            st.metric("Technical Score", f"{a_breakdown.get('Technical_Score', 0):.2f}", delta=f"{(a_breakdown.get('Technical_Score', 0) - b_breakdown.get('Technical_Score', 0)):.2f}")
            st.metric("Experience Score", f"{a_breakdown.get('Experience_Score', 0):.2f}", delta=f"{(a_breakdown.get('Experience_Score', 0) - b_breakdown.get('Experience_Score', 0)):.2f}")
            st.metric("Behavior Score", f"{a_breakdown.get('Behavior_Score', 0):.2f}", delta=f"{(a_breakdown.get('Behavior_Score', 0) - b_breakdown.get('Behavior_Score', 0)):.2f}")
            st.metric("Market Score", f"{a_breakdown.get('Market_Score', 0):.2f}", delta=f"{(a_breakdown.get('Market_Score', 0) - b_breakdown.get('Market_Score', 0)):.2f}")
            
        with colB:
            st.subheader(f"🏆 Candidate B: {cand_b_id}")
            st.markdown(f"**Overall Rank**: {cand_b['rank']} (Score: {cand_b['score']:.4f})")
            st.metric("Technical Score", f"{b_breakdown.get('Technical_Score', 0):.2f}", delta=f"{(b_breakdown.get('Technical_Score', 0) - a_breakdown.get('Technical_Score', 0)):.2f}")
            st.metric("Experience Score", f"{b_breakdown.get('Experience_Score', 0):.2f}", delta=f"{(b_breakdown.get('Experience_Score', 0) - a_breakdown.get('Experience_Score', 0)):.2f}")
            st.metric("Behavior Score", f"{b_breakdown.get('Behavior_Score', 0):.2f}", delta=f"{(b_breakdown.get('Behavior_Score', 0) - a_breakdown.get('Behavior_Score', 0)):.2f}")
            st.metric("Market Score", f"{b_breakdown.get('Market_Score', 0):.2f}", delta=f"{(b_breakdown.get('Market_Score', 0) - a_breakdown.get('Market_Score', 0)):.2f}")
            
        st.markdown("---")
        st.subheader("Verdict Summary")
        if cand_a['score'] > cand_b['score']:
            st.success(f"**{cand_a_id}** is ranked higher. While both candidates may have strengths, Candidate A achieved a total weighted score of {cand_a['score']:.4f} compared to {cand_b_id}'s {cand_b['score']:.4f}.")
        elif cand_b['score'] > cand_a['score']:
            st.success(f"**{cand_b_id}** is ranked higher. While both candidates may have strengths, Candidate B achieved a total weighted score of {cand_b['score']:.4f} compared to {cand_a_id}'s {cand_a['score']:.4f}.")
        else:
            st.info("Both candidates achieved the exact same weighted score.")
