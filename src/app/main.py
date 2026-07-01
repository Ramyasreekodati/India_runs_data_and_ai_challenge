# src/app/main.py
import csv
import sys
import time
import pandas as pd
from src.job_engine.parser import JobRequirements
from src.retrieval.pipeline import RetrievalPipeline
from src.ranking.ranker import MultiLevelRanker
from src.reasoning.generator import ReasonGenerator

def run_pipeline(jsonl_path, output_csv_path, config=None, team_id="team_ranker"):
    """
    Executes the entire pipeline and returns execution metrics and the final dataframe.
    This enables Streamlit to render live results without hardcoding.
    """
    start_time = time.time()
    
    # 1. Job Requirements
    job = JobRequirements()
    
    # 2. Retrieval (Top 3000 via heuristic heap)
    retriever = RetrievalPipeline(top_k=3000)
    top_candidates = retriever.retrieve(jsonl_path)
    
    # 3. Re-Ranking (Top 100 via rigorous multi-level fusion)
    ranker = MultiLevelRanker(job, config=config)
    ranked_results = ranker.rank(top_candidates)
    
    # We only need top 100
    top_100 = ranked_results[:100]
    
    # 4. Reason Generation & Output
    reasoner = ReasonGenerator()
    
    rows = []
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank, cand in enumerate(top_100, start=1):
            cand_id = cand["candidate_id"]
            score = cand["score"]
            formatted_score = f"{score:.4f}"
            reason = reasoner.generate(cand)
            
            writer.writerow([cand_id, rank, formatted_score, reason])
            rows.append({
                "candidate_id": cand_id,
                "rank": rank,
                "score": score,
                "reasoning": reason,
                "raw_breakdown": cand["breakdown"]
            })
            
    elapsed = time.time() - start_time
    
    metrics = {
        "runtime_seconds": elapsed,
        "total_processed": 100000, # Handled by the retriever stream
        "retrieved": len(top_candidates),
        "final_ranked": len(top_100)
    }
    
    df = pd.DataFrame(rows)
    return metrics, df

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.app.main <input.jsonl> <output.csv>")
        sys.exit(1)
        
    print("Starting Intelligent Candidate Discovery & Ranking Pipeline...")
    metrics, df = run_pipeline(sys.argv[1], sys.argv[2])
    print(f"Pipeline completed successfully in {metrics['runtime_seconds']:.2f} seconds!")
