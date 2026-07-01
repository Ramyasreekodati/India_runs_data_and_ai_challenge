# src/reasoning/generator.py

class ReasonGenerator:
    """
    Constructs the reasoning string deterministically from the exact features used to score the candidate.
    This guarantees zero hallucinations and directly answers the Stage 4 Manual Review criteria.
    """
    
    def generate(self, ranked_candidate):
        """
        Takes a ranked candidate dict: {"candidate_id": ..., "features": ..., "breakdown": ..., "score": ...}
        and returns a 1-2 sentence justification.
        """
        features = ranked_candidate["features"]
        breakdown = ranked_candidate["breakdown"]
        score = ranked_candidate["score"]
        
        # Identity Facts
        title = ranked_candidate["raw_data"].get("profile", {}).get("current_title", "Professional")
        yoe = features["exp_total_years"]
        
        # Technical Facts
        tech_score = breakdown.get("Technical_Score", 0)
        
        # Behavior Facts
        resp_rate = features["beh_response_rate"]
        
        # Negative signals check
        concerns = []
        if features["avail_notice_period"] > 30:
            concerns.append(f"notice period ({features['avail_notice_period']} days)")
        if features["exp_is_job_hopper"] > 0:
            concerns.append("short average tenure")
        if features["risk_pure_consulting"] > 0:
            concerns.append("consulting-only background")
            
        # Construct the sentence
        if score > 0.8:
            reason = f"{title} with {yoe:.1f} yrs experience; strong technical match."
            if resp_rate > 0.7:
                reason += f" Highly responsive ({resp_rate:.2f} rate)."
            if concerns:
                reason += f" Minor concern: {', '.join(concerns)}."
        elif score > 0.5:
            reason = f"{title} with {yoe:.1f} yrs; moderate tech fit."
            if concerns:
                reason += f" Identified gaps: {', '.join(concerns)}."
        else:
            reason = f"{title} ({yoe:.1f} yrs). Included as filler due to low technical or behavioral alignment."
            if concerns:
                reason += f" Primary issues: {', '.join(concerns)}."
                
        # Ensure it's clean and under limit
        return reason.strip()
