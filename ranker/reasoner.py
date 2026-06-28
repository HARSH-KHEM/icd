from datetime import datetime, timezone

def generate_reasoning(candidates: list) -> list:
    for i, c in enumerate(candidates):
        rank = i + 1
        prof = c.get('profile', {})
        yoe = prof.get('years_of_experience', 0)
        title = prof.get('current_title', 'Unknown')
        company = prof.get('current_company', 'Unknown')
        
        # Sentence 1: Core Fit
        s1 = f"{yoe} years of experience; {title} at {company}."
        
        rel_skills = []
        for s in c.get('skills', []):
            name_lower = s.get('name', '').lower()
            if any(kw in name_lower for kw in ['embedding', 'retrieval', 'vector', 'search', 'llm']):
                rel_skills.append((s.get('name'), s.get('proficiency')))
        
        if rel_skills:
            rel_skills.sort(key=lambda x: ['beginner', 'intermediate', 'advanced', 'expert'].index(x[1].lower()) if x[1].lower() in ['beginner', 'intermediate', 'advanced', 'expert'] else 0, reverse=True)
            top_2 = rel_skills[:2]
            skills_str = ", ".join([f"{name} ({prof})" for name, prof in top_2])
            s1 += f" Strong skills in {skills_str}."
            
        has_product = False
        services_keywords = ["product", "platform", "shipped", "launched", "built", "designed", "architected", "owned"]
        for job in c.get('career_history', []):
            desc = job.get('description', '').lower()
            if any(kw in desc for kw in services_keywords):
                has_product = True
                break
        if has_product:
            s1 += " Has product company background."
            
        # Sentence 2: Signals + concerns
        s2 = ""
        signals = c.get('redrob_signals', {})
        
        # Date parsing
        now = datetime.now(timezone.utc)
        last_active = signals.get('last_active_date')
        days_ago = 999
        if last_active:
            try:
                last_active_dt = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                days_ago = (now - last_active_dt).days
            except:
                pass
                
        open_to_work = signals.get('open_to_work_flag', False)
        notice_period = signals.get('notice_period_days', 90)
        location = prof.get('location', '')
        loc_match = any(l in location for l in ["Pune", "Noida", "Delhi", "Hyderabad", "Mumbai", "Bangalore", "Bengaluru", "Gurugram", "Gurgaon"])
        willing_to_relocate = signals.get('willing_to_relocate', False)
        rrr = signals.get('recruiter_response_rate', 0.5)
        
        if open_to_work and days_ago < 30:
            s2 = "Actively looking, recently active on platform."
        elif notice_period <= 30:
            s2 = f"Short notice period ({notice_period} days)."
        elif notice_period > 90:
            s2 = f"Long notice period ({notice_period} days) is a concern."
        elif loc_match:
            s2 = f"Based in {location}, matches role location."
        elif not loc_match and not willing_to_relocate:
            s2 = f"Located in {location}, not willing to relocate — potential concern."
        elif days_ago > 180:
            s2 = "Has not been active on platform in over 6 months — availability uncertain."
        elif rrr < 0.2:
            s2 = f"Low recruiter response rate ({rrr}) may indicate passive candidate."
            
        # Ensure tone matches rank
        if rank <= 10:
            if not s2:
                s2 = "Strong overall profile for this role."
        elif rank <= 50:
            if not s2:
                s2 = "Solid candidate with balanced experience."
        else:
            if "concern" not in s2.lower() and "uncertain" not in s2.lower() and "passive" not in s2.lower():
                s2 = "Meets basic criteria, but lacks strong recent signals or perfect location match."
                
        c['_reasoning'] = f"{s1} {s2}".strip()
        
    return candidates
