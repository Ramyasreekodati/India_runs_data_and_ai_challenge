# src/retrieval/pipeline.py
import heapq
import time
from src.candidate_engine.parser import parse_candidate
from src.feature_engineering.extractor import FeatureExtractor
from src.app.loaders import CandidateLoader

class RetrievalPipeline:
    def __init__(self, job_reqs, top_k=3000):
        self.top_k = top_k
        self.job_reqs = job_reqs
        self.extractor = FeatureExtractor(self.job_reqs)
        
    def retrieve(self, jsonl_path):
        """
        Streams the large JSONL dataset and returns the Top K candidates based on the fast heuristic score.
        Uses a min-heap to keep memory constant.
        """
        top_candidates = [] # heap of (score, candidate_id, raw_dict, features)
        
        start_time = time.time()
        processed = 0
        
        loader = CandidateLoader(jsonl_path)
        
        for raw in loader.stream():
            processed += 1
            cand = parse_candidate(raw)
            features = self.extractor.extract(cand)
            score = self.extractor.compute_heuristic_score(features)
            
            # Only push to heap if we don't have top_k yet, or if score is better than the worst in our top_k
            if len(top_candidates) < self.top_k:
                heapq.heappush(top_candidates, (score, cand.id, raw, features))
            elif score > top_candidates[0][0]:
                heapq.heapreplace(top_candidates, (score, cand.id, raw, features))
                    
        elapsed = time.time() - start_time
        print(f"Retrieval Pipeline: Processed {processed} candidates in {elapsed:.2f}s. Kept top {len(top_candidates)}.")
        
        # Sort descending by score
        top_candidates.sort(key=lambda x: x[0], reverse=True)
        return top_candidates
