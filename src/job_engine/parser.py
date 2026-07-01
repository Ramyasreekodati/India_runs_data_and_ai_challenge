# src/job_engine/parser.py

class JobRequirements:
    """
    Structured representation of the Job Description.
    Instead of keyword matching, we define specific hard requirements and disqualifiers.
    """
    def __init__(self):
        # 1. Mandatory Technical Skills
        self.mandatory_skills = [
            {"category": "retrieval", "keywords": ["sentence-transformers", "openai embeddings", "bge", "e5", "retrieval", "rag"]},
            {"category": "vector_db", "keywords": ["pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss"]},
            {"category": "language", "keywords": ["python"]},
            {"category": "evaluation", "keywords": ["ndcg", "mrr", "map", "a/b test", "evaluation"]}
        ]

        # 2. Preferred Skills
        self.preferred_skills = [
            {"category": "finetuning", "keywords": ["lora", "qlora", "peft", "fine-tuning"]},
            {"category": "ltr", "keywords": ["learning-to-rank", "xgboost"]},
            {"category": "domain", "keywords": ["hr-tech", "recruiting", "marketplace"]},
            {"category": "systems", "keywords": ["distributed systems", "large-scale"]}
        ]

        # 3. Disqualifiers (Negative Signals)
        self.disqualifying_companies = [
            "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"
        ] # Must penalize if ONLY these companies exist in history

        self.disqualifying_personas = [
            "research_only",  # academia, researcher, no production
            "framework_only", # only langchain, no core ml
            "non_coding_architect" # architect title for last 1.5+ years without coding
        ]

        # 4. Experience & Logistics
        self.ideal_yoe_min = 4.0
        self.ideal_yoe_max = 10.0
        self.preferred_locations = ["pune", "noida", "delhi ncr", "mumbai", "hyderabad"]
        self.max_notice_period = 30 # sub 30 preferred, >30 tolerable but lower score

    def evaluate_candidate(self, candidate_features):
        """
        Takes a candidate's structured features and scores them against this JD.
        To be implemented in the multi-level ranking engine.
        """
        pass
