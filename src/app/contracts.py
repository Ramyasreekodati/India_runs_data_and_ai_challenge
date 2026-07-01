# src/app/contracts.py
from dataclasses import dataclass
import pandas as pd
from typing import Dict, Any

@dataclass
class PipelineResults:
    job_analysis: Dict[str, Any]
    dataset_analysis: Dict[str, Any]
    feature_summary: Dict[str, Any]
    retrieval_funnel: Dict[str, Any]
    profiling: Dict[str, Any]
    validation_passed: bool
    top_candidates: pd.DataFrame
