def rerank_candidates(candidates: list, top_k: int = 100) -> list:
    for c in candidates:
        yoe = c.get('profile', {}).get('years_of_experience', 0)
        
        # Experience Score
        exp_score = 0.3
        if 5 <= yoe <= 9:
            exp_score = 1.0
        elif 3 <= yoe < 5:
            exp_score = 0.6
        elif 9 < yoe <= 12:
            exp_score = 0.8
            
        has_non_services = False
        for job in c.get('career_history', []):
            if job.get('company_size') != '10001+' and job.get('industry') not in ["IT Services", "Consulting"]:
                has_non_services = True
                break
        if has_non_services:
            exp_score += 0.1
            
        education_tier = next((edu.get('tier') for edu in c.get('education', [])), None)
        if education_tier in ["tier_1", "tier_2"]:
            exp_score += 0.05
            
        cert_issuers = [cert.get('issuer', '') for cert in c.get('certifications', [])]
        known_issuers = ["Google", "AWS", "Coursera", "DeepLearning.AI", "Nvidia", "Microsoft"]
        if any(issuer in known_issuers for issuer in cert_issuers):
            exp_score += 0.05
            
        exp_score = min(1.0, exp_score)
        c['_experience_score'] = exp_score
        
        # Behavioral Score
        beh_score = 0.5
        signals = c.get('redrob_signals', {})
        
        if signals.get('open_to_work_flag'):
            beh_score += 0.15
            
        # Mocking last_active_date logic since we don't have current time in data
        # Assuming current time is end of 2024 or similar, we'll just check if it exists
        # To be robust, let's parse it if possible, otherwise skip date logic
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        last_active = signals.get('last_active_date')
        if last_active:
            try:
                # Basic ISO parse
                last_active_dt = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                days_ago = (now - last_active_dt).days
                if days_ago <= 30:
                    beh_score += 0.15
                elif days_ago <= 90:
                    beh_score += 0.05
                elif days_ago > 180:
                    beh_score -= 0.20
            except:
                pass

        rrr = signals.get('recruiter_response_rate', 0)
        if rrr > 0.7:
            beh_score += 0.10
        elif rrr > 0.4:
            beh_score += 0.05
        elif rrr < 0.2:
            beh_score -= 0.15
            
        np = signals.get('notice_period_days', 90)
        if np <= 30:
            beh_score += 0.10
        elif np <= 60:
            beh_score += 0.05
        elif np > 90:
            beh_score -= 0.10
            
        gh = signals.get('github_activity_score', -1)
        if gh > 70:
            beh_score += 0.10
        elif gh > 40:
            beh_score += 0.05
            
        icr = signals.get('interview_completion_rate', 0.5)
        if icr > 0.8:
            beh_score += 0.05
        elif icr < 0.4:
            beh_score -= 0.05
            
        if signals.get('verified_email') and signals.get('verified_phone'):
            beh_score += 0.05
            
        if signals.get('profile_completeness_score', 0) > 80:
            beh_score += 0.05
            
        beh_score = max(0.0, min(1.0, beh_score))
        c['_behavioral_score'] = beh_score
        
        # Context Score
        ctx_score = 0.5
        loc = c.get('profile', {}).get('location', '')
        country = c.get('profile', {}).get('country', '')
        
        loc_match = any(l in loc for l in ["Pune", "Noida", "Delhi", "Hyderabad", "Mumbai", "Bangalore", "Bengaluru", "Gurugram", "Gurgaon"])
        if loc_match:
            ctx_score += 0.3
            
        if signals.get('willing_to_relocate') and country == "India":
            ctx_score += 0.15
            
        if signals.get('preferred_work_mode') in ["hybrid", "flexible", "onsite"]:
            ctx_score += 0.10
            
        salary = signals.get('expected_salary_range_inr_lpa', {})
        if salary.get('max', 100) < 15:
            ctx_score -= 0.10
        if salary.get('min', 0) > 80:
            ctx_score -= 0.10
            
        ctx_score = max(0.0, min(1.0, ctx_score))
        c['_context_score'] = ctx_score
        
        # Final Score
        c['_final_score'] = (
            0.35 * c['_semantic_score'] +
            0.25 * c['_experience_score'] +
            0.25 * c['_behavioral_score'] +
            0.15 * c['_context_score']
        )
        
    candidates.sort(key=lambda x: x['_final_score'], reverse=True)
    return candidates[:top_k]
