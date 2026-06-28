from datetime import datetime
import re

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def filter_candidates(candidates: list) -> list:
    filtered = []
    
    keywords = ["ml", "machine learning", "ai", "artificial intelligence", "nlp", "embedding", 
                "vector", "retrieval", "ranking", "recommendation", "search", "llm", 
                "transformer", "deep learning", "neural", "pytorch", "tensorflow", "scikit", 
                "bert", "gpt", "rag", "fine-tun", "faiss", "elasticsearch", "semantic"]
    
    services_keywords = ["product", "platform", "shipped", "launched", "built", "designed", "architected", "owned"]
    
    for candidate in candidates:
        candidate['_filter_passed'] = False
        candidate['_honeypot_flag'] = False
        
        # Honeypot Check
        is_honeypot = False
        total_career_months = 0
        
        for job in candidate.get('career_history', []):
            start = parse_date(job.get('start_date', ''))
            end = parse_date(job.get('end_date', ''))
            duration = job.get('duration_months', 0)
            
            if start:
                if start.year < 1990: # Simple plausible date check
                    is_honeypot = True
                    break
                if end:
                    actual_months = (end.year - start.year) * 12 + (end.month - start.month)
                    if abs(actual_months - duration) > 6:
                        is_honeypot = True
                        break
            total_career_months += duration
            
        if is_honeypot:
            candidate['_honeypot_flag'] = True
            continue
            
        expert_stuffing_count = 0
        for skill in candidate.get('skills', []):
            if skill.get('proficiency') == 'expert' and skill.get('endorsements', 0) == 0 and skill.get('duration_months', 0) == 0:
                expert_stuffing_count += 1
        
        if expert_stuffing_count > 8:
            candidate['_honeypot_flag'] = True
            continue
            
        yoe = candidate.get('profile', {}).get('years_of_experience', 0)
        if yoe > (total_career_months / 12) + 3:
            candidate['_honeypot_flag'] = True
            continue
            
        # Experience Check
        if yoe < 3 or yoe > 16:
            continue
            
        # Role description keywords check
        role_kws = ['embedding', 'vector', 'retrieval', 'ranking', 'recommendation', 'search', 'llm', 'transformer', 'bert', 'faiss', 'elasticsearch', 'semantic', 'rag', 'fine-tun', 'neural', 'pytorch', 'tensorflow']
        has_role_match = False
        for job in candidate.get('career_history', []):
            desc = job.get('description', '').lower()
            matched = sum(1 for kw in role_kws if kw in desc)
            if matched >= 2:
                has_role_match = True
                break
        if not has_role_match:
            continue
            
        # Title check
        title_kws = ['engineer', 'scientist', 'researcher', 'ml', 'ai', 'data', 'nlp', 'architect']
        curr_title = candidate.get('profile', {}).get('current_title', '').lower()
        title_match = any(kw in curr_title for kw in title_kws)
        if not title_match:
            for job in candidate.get('career_history', []):
                title = job.get('title', '').lower()
                if any(kw in title for kw in title_kws):
                    title_match = True
                    break
        if not title_match:
            continue
            
        # Skill check
        skill_kws = ['python', 'machine learning', 'deep learning', 'nlp', 'pytorch', 'tensorflow', 'bert', 'transformers', 'embedding', 'vector', 'faiss', 'elasticsearch', 'recommendation', 'ranking', 'retrieval', 'llm', 'rag', 'fine-tuning', 'scikit-learn', 'keras']
        matched_skills = sum(1 for skill in candidate.get('skills', []) if any(kw in skill.get('name', '').lower() for kw in skill_kws))
        if matched_skills < 2:
            continue
            
        # Pure Services Disqualification
        career_history = candidate.get('career_history', [])
        all_companies_services = True
        for job in career_history:
            if not (job.get('company_size') == '10001+' or job.get('industry') in ["IT Services", "Consulting", "Outsourcing"]):
                all_companies_services = False
                break
                
        current_industry = candidate.get('profile', {}).get('current_industry', '')
        is_current_services = current_industry in ["IT Services", "Consulting", "Outsourcing"]
        
        has_product_keyword = False
        for job in career_history:
            desc = job.get('description', '').lower()
            if any(kw in desc for kw in services_keywords):
                has_product_keyword = True
                break
                
        if all_companies_services and is_current_services and not has_product_keyword:
            continue
            
        candidate['_filter_passed'] = True
        filtered.append(candidate)
        
    return filtered
