# src/app/loaders.py
import json
import os

class CandidateLoader:
    """
    Abstracts the loading of candidates from various file formats.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def stream(self):
        """
        Yields raw candidate dictionaries one by one.
        Handles both standard JSON arrays and JSONL files.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Cannot find dataset at {self.file_path}")
            
        # Robustly detect if it's a JSON array or JSONL
        is_json_array = False
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    if stripped.startswith("["):
                        is_json_array = True
                    break
        
        with open(self.file_path, "r", encoding="utf-8-sig") as f:
            if is_json_array:
                # Load the whole array and yield items
                data = json.load(f)
                for item in data:
                    yield item
            else:
                # Stream JSONL
                for line in f:
                    if not line.strip(): continue
                    yield json.loads(line)

class JobLoader:
    """
    Loads Job Requirements from a configuration dictionary, or uses defaults.
    """
    @staticmethod
    def load_requirements(custom_config=None):
        from src.job_engine.parser import JobRequirements
        
        job = JobRequirements()
        
        if custom_config:
            if "mandatory_skills" in custom_config:
                job.mandatory_skills = custom_config["mandatory_skills"]
            if "preferred_skills" in custom_config:
                job.preferred_skills = custom_config["preferred_skills"]
            if "disqualifying_personas" in custom_config:
                job.disqualifying_personas = custom_config["disqualifying_personas"]
            if "disqualifying_companies" in custom_config:
                job.disqualifying_companies = custom_config["disqualifying_companies"]
                
        return job
