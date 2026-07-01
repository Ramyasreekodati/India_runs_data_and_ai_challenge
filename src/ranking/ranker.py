# src/ranking/ranker.py

class MultiLevelRanker:
    def __init__(self, job_reqs):
        self.job = job_reqs
        
    def score_candidate(self, features):
        """
        Computes independent scores based on the extracted features, and fuses them into a final score.
        Returns a tuple: (final_score, breakdown_dict)
        """
        # If honeypot, hard fail.
        if features.get("risk_is_honeypot", 0) > 0:
            return 0.0, {"risk_failure": True}
            
        breakdown = {}
        
        # 1. Technical Score (0 to 1) - Heavily weighted
        # Reward mandatory matching and preferred matching.
        tech_score = (features["tech_mandatory_match_ratio"] * 0.7) + (features["tech_preferred_match_ratio"] * 0.3)
        if features["tech_is_ai_title"] > 0:
            tech_score = min(1.0, tech_score + 0.1) # Boost for actual AI titles
        breakdown["Technical_Score"] = tech_score
        
        # 2. Experience & Production Score (0 to 1)
        # 5-9 years is ideal. We normalize based on the ideal range.
        exp = features["exp_total_years"]
        if self.job.ideal_yoe_min <= exp <= self.job.ideal_yoe_max:
            exp_score = 1.0
        elif exp < self.job.ideal_yoe_min:
            # linear penalty for being too junior
            exp_score = max(0.0, exp / self.job.ideal_yoe_min)
        else:
            # minor penalty for being too senior (overqualified / potentially management)
            exp_score = max(0.0, 1.0 - ((exp - self.job.ideal_yoe_max) * 0.05))
            
        # Penalize job hoppers
        if features["exp_is_job_hopper"] > 0:
            exp_score *= 0.7
            
        breakdown["Experience_Score"] = exp_score
        
        # 3. Behavior & Availability Score (0 to 1)
        # Combines recruiter response, github presence, profile completeness, and notice period
        beh_score = (features["beh_response_rate"] * 0.4) + \
                    (features["beh_has_github"] * 0.2) + \
                    (features["beh_profile_completeness"] * 0.2) + \
                    (features["avail_good_notice"] * 0.2)
        breakdown["Behavior_Score"] = beh_score
        
        # 4. Market Interest Score (0 to 1)
        # Logarithmic scaling of search appearances and recruiter saves
        mkt_saves = features["mkt_saved_by_recruiters"]
        mkt_searches = features["mkt_search_appearances"]
        
        # Assuming typical top saves is around ~20, searches around ~50 in 30 days
        mkt_score = min(1.0, (mkt_saves / 20.0) * 0.6 + (mkt_searches / 50.0) * 0.4)
        breakdown["Market_Score"] = mkt_score
        
        # 5. Weighted Fusion
        # Determine fusion weights based on the job requirements priority
        # JD emphasizes: Technical Depth (Mandatory), Production Experience, and availability
        final_score = (
            breakdown["Technical_Score"] * 0.45 +
            breakdown["Experience_Score"] * 0.25 +
            breakdown["Behavior_Score"] * 0.20 +
            breakdown["Market_Score"] * 0.10
        )
        
        # Apply continuous penalties
        if features.get("risk_is_keyword_stuffer", 0) > 0:
            final_score *= 0.5 # Severe penalty, but not a hard drop
            
        if features.get("risk_pure_consulting", 0) > 0:
            final_score *= 0.8
            
        if features.get("risk_low_response", 0) > 0:
            final_score *= 0.9
            
        # Guarantee monotonic behavior by normalizing against maximum possible 1.0
        final_score = max(0.0, min(1.0, final_score))
        breakdown["Final_Score"] = final_score
        
        return final_score, breakdown
        
    def rank(self, top_candidates):
        """
        Takes the heap of top candidates from retrieval (score, id, raw, features)
        and re-ranks them using the exact multi-level scoring fusion.
        """
        ranked_results = []
        
        for heur_score, cand_id, raw, features in top_candidates:
            final_score, breakdown = self.score_candidate(features)
            # Round to 4 decimal places to ensure tie-breaks work as expected
            final_score = round(final_score, 4)
            ranked_results.append({
                "candidate_id": cand_id,
                "raw_data": raw,
                "features": features,
                "breakdown": breakdown,
                "score": final_score
            })
            
        # Sort descending by Final_Score. If tie, sort by candidate_id ascending to satisfy validator.
        ranked_results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
        
        return ranked_results
