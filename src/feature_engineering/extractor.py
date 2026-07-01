# src/feature_engineering/extractor.py
import math

class FeatureExtractor:
    """
    Transforms CandidateFeatures and JobRequirements into a dense feature vector (or dictionary of scores)
    for downstream ranking.
    """
    def __init__(self, job_reqs):
        self.job = job_reqs

    def extract(self, cand):
        features = {}
        # 1. RISK FEATURES (Continuous penalties instead of hard drops)
        features["risk_is_honeypot"] = 1.0 if cand.is_honeypot else 0.0
        features["risk_is_keyword_stuffer"] = 1.0 if cand.is_keyword_stuffer else 0.0
        
        # Calculate pure consulting risk as a ratio if they only have consulting
        features["risk_pure_consulting"] = 1.0 if cand.is_pure_consulting else 0.0
        
        features["risk_low_response"] = 1.0 if cand.response_rate < 0.2 else 0.0
        features["risk_inactive"] = 1.0 if cand.signals.get("last_active_date", "") < "2025-01-01" else 0.0
        
        # 2. TECHNICAL FEATURES
        # Match mandatory skill categories
        mandatory_matched = 0
        for req in self.job.mandatory_skills:
            # Check if any candidate skill matches any keyword in this category
            if any(kw in cand.skill_names for kw in req["keywords"]):
                mandatory_matched += 1
                features[f"tech_has_{req['category']}"] = 1.0
            else:
                features[f"tech_has_{req['category']}"] = 0.0
                
        features["tech_mandatory_match_ratio"] = mandatory_matched / len(self.job.mandatory_skills) if self.job.mandatory_skills else 0
        
        preferred_matched = 0
        for req in self.job.preferred_skills:
            if any(kw in cand.skill_names for kw in req["keywords"]):
                preferred_matched += 1
                features[f"tech_has_{req['category']}"] = 1.0
            else:
                features[f"tech_has_{req['category']}"] = 0.0
                
        features["tech_preferred_match_ratio"] = preferred_matched / len(self.job.preferred_skills) if self.job.preferred_skills else 0
        
        # AI Title boost
        ai_titles = ["ai", "machine learning", "ml ", "data scientist"]
        features["tech_is_ai_title"] = 1.0 if any(t in cand.current_title for t in ai_titles) else 0.0
        
        # 3. EXPERIENCE FEATURES
        features["exp_total_years"] = cand.years_of_experience
        features["exp_years_in_ideal_range"] = 1.0 if (self.job.ideal_yoe_min <= cand.years_of_experience <= self.job.ideal_yoe_max) else 0.0
        features["exp_avg_tenure"] = cand.average_tenure
        features["exp_is_job_hopper"] = 1.0 if (cand.average_tenure < 1.5 and cand.years_of_experience > 3) else 0.0
        
        # 4. BEHAVIOR & AVAILABILITY FEATURES
        features["beh_response_rate"] = cand.response_rate
        features["beh_github_score"] = cand.github_score if cand.github_score >= 0 else 0
        features["beh_has_github"] = 1.0 if cand.github_score >= 0 else 0.0
        features["beh_profile_completeness"] = cand.signals.get("profile_completeness_score", 0) / 100.0
        
        features["avail_notice_period"] = cand.notice_period
        features["avail_good_notice"] = 1.0 if cand.notice_period <= self.job.max_notice_period else 0.0
        features["avail_open_to_work"] = 1.0 if cand.signals.get("open_to_work_flag", False) else 0.0
        
        # 5. MARKET INTEREST
        features["mkt_saved_by_recruiters"] = cand.signals.get("saved_by_recruiters_30d", 0)
        features["mkt_search_appearances"] = cand.signals.get("search_appearance_30d", 0)
        features["mkt_interview_completion"] = cand.signals.get("interview_completion_rate", 0)
        
        return features

    def compute_heuristic_score(self, features):
        """
        Computes a fast heuristic score based on the extracted features.
        Useful for the initial retrieval filtering step.
        """
        if features["risk_is_honeypot"] > 0:
            return 0.0 # Honeypots are still an instant drop per competition rules
            
        base_score = 0.0
        
        # Tech (40%)
        base_score += features["tech_mandatory_match_ratio"] * 0.30
        base_score += features["tech_preferred_match_ratio"] * 0.10
        base_score += features["tech_is_ai_title"] * 0.10
        
        # Experience (20%)
        if features["exp_years_in_ideal_range"]:
            base_score += 0.15
        elif features["exp_total_years"] >= self.job.ideal_yoe_min:
            base_score += 0.05
            
        if features["exp_is_job_hopper"]:
            base_score -= 0.10
            
        # Behavior (25%)
        base_score += features["beh_response_rate"] * 0.15
        base_score += (features["beh_github_score"] / 100.0) * 0.10
        
        # Availability & Market (15%)
        base_score += features["avail_good_notice"] * 0.05
        base_score += features["avail_open_to_work"] * 0.05
        # normalize market signals via log to prevent massive outlier domination
        base_score += min(0.05, math.log1p(features["mkt_saved_by_recruiters"]) * 0.01)

        # Apply continuous penalties
        if features["risk_is_keyword_stuffer"]:
            base_score *= 0.5 # Severe penalty, but not a hard drop
            
        if features["risk_pure_consulting"]:
            base_score *= 0.8
            
        if features["risk_low_response"]:
            base_score *= 0.9
            
        return max(0.0, min(1.0, base_score))
