# src/app/contracts.py
from dataclasses import dataclass
import pandas as pd

@dataclass
class JobAnalysis:
    mandatory_skills_count: int
    preferred_skills_count: int
    disqualifying_personas_count: int

@dataclass
class DatasetProfile:
    total_processed: int
    ai_titles_detected: int
    keyword_stuffers_flagged: int
    missing_values_rate: str

@dataclass
class RetrievalResults:
    total_processed: int
    heuristic_pass: int
    retrieved_top_k: int
    final_ranked: int

@dataclass
class FeatureSummary:
    technical: int
    behavior: int
    experience: int
    risk: int
    market: int

@dataclass
class EvaluationResults:
    runtime_seconds: float
    peak_memory_mb: float
    validator_passed: bool

@dataclass
class PipelineResults:
    job_analysis: JobAnalysis
    dataset_analysis: DatasetProfile
    feature_summary: FeatureSummary
    retrieval_funnel: RetrievalResults
    profiling: EvaluationResults
    top_candidates: pd.DataFrame
