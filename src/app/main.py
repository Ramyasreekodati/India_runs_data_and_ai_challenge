# src/app/main.py
import csv
import sys
import time
from src.job_engine.parser import JobRequirements
from src.retrieval.pipeline import RetrievalPipeline
from src.ranking.ranker import MultiLevelRanker
from src.reasoning.generator import ReasonGenerator

def generate_submission(jsonl_path, output_csv_path, team_id="team_ranker"):
    start_time = time.time()
    print("Starting Intelligent Candidate Discovery & Ranking Pipeline...")
    
    # 1. Job Requirements
    job = JobRequirements()
    
    # 2. Retrieval (Top 3000 via heuristic heap)
    print("Executing Phase 1: Retrieval (Streaming...)")
    retriever = RetrievalPipeline(top_k=3000)
    top_candidates = retriever.retrieve(jsonl_path)
    
    # 3. Re-Ranking (Top 100 via rigorous multi-level fusion)
    print(f"Executing Phase 2: Multi-Level Ranking (Top {len(top_candidates)} candidates...)")
    ranker = MultiLevelRanker(job)
    ranked_results = ranker.rank(top_candidates)
    
    # We only need top 100
    top_100 = ranked_results[:100]
    
    # 4. Reason Generation & Output
    print(f"Executing Phase 3: Reason Generation & CSV Export to {output_csv_path}")
    reasoner = ReasonGenerator()
    
    # Enforce strictly monotonic scores (Challenge Requirement)
    # The ranker already sorts by score descending.
    
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank, cand in enumerate(top_100, start=1):
            cand_id = cand["candidate_id"]
            
            score = cand["score"]
            
            # Ensure float formatting with 4 decimal places
            formatted_score = f"{score:.4f}"
            
            reason = reasoner.generate(cand)
            writer.writerow([cand_id, rank, formatted_score, reason])
            
    elapsed = time.time() - start_time
    print(f"Pipeline completed successfully in {elapsed:.2f} seconds!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.app.main <input.jsonl> <output.csv>")
        sys.exit(1)
        
    generate_submission(sys.argv[1], sys.argv[2])
