# src/candidate_engine/parser.py

class CandidateFeatures:
    """
    Structured representation of a candidate's features.
    """
    def __init__(self, raw_data):
        self.raw = raw_data
        self.id = raw_data.get("candidate_id")
        self.profile = raw_data.get("profile", {})
        self.career = raw_data.get("career_history", [])
        self.education = raw_data.get("education", [])
        self.skills = raw_data.get("skills", [])
        self.signals = raw_data.get("redrob_signals", {})
        
        # 1. Identity & Profile
        self.current_title = self.profile.get("current_title", "").lower()
        self.current_company = self.profile.get("current_company", "").lower()
        self.location = self.profile.get("location", "").lower()
        
        # 2. Experience
        self.years_of_experience = self.profile.get("years_of_experience", 0)
        self.total_companies = len(self.career)
        self.average_tenure = (self.years_of_experience / self.total_companies) if self.total_companies > 0 else 0
        
        # 3. Technical Skills Extraction
        self.skill_names = set([s.get("name", "").lower() for s in self.skills])
        self.expert_skills = set([s.get("name", "").lower() for s in self.skills if s.get("proficiency") == "expert"])
        
        # Determine if they have any mandatory skills from JD
        self.has_python = "python" in self.skill_names
        
        # 4. Behavioral & Market Signals
        self.response_rate = self.signals.get("recruiter_response_rate", 0)
        self.github_score = self.signals.get("github_activity_score", -1)
        self.notice_period = self.signals.get("notice_period_days", 90)
        
        # 5. Risk / Traps
        self.is_keyword_stuffer = self._check_keyword_stuffer()
        self.is_honeypot = self._check_honeypot()
        self.is_pure_consulting = self._check_pure_consulting()
        
    def _check_keyword_stuffer(self):
        # E.g. "Marketing Manager" with "RAG", "LLM"
        non_tech_titles = ["marketing", "hr ", "human resources", "sales", "accountant", "customer support"]
        is_non_tech = any(t in self.current_title for t in non_tech_titles)
        
        ai_keywords = {"rag", "pinecone", "llm", "embeddings"}
        has_ai_skills = len(self.skill_names.intersection(ai_keywords)) > 0
        
        return is_non_tech and has_ai_skills

    def _check_honeypot(self):
        # Honeypot: "expert" proficiency in skills with 0 years used
        expert_0_yrs_count = 0
        for s in self.skills:
            if s.get("proficiency") == "expert" and s.get("duration_months", 1) == 0:
                expert_0_yrs_count += 1
        return expert_0_yrs_count >= 5

    def _check_pure_consulting(self):
        consulting_firms = {"tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"}
        if not self.career:
            return False
            
        companies_worked = set([job.get("company", "").lower() for job in self.career])
        # If all their companies are in the consulting_firms list
        return companies_worked.issubset(consulting_firms)

def parse_candidate(raw_dict):
    return CandidateFeatures(raw_dict)
