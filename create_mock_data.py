import gzip
import json
import random

def generate_mock_data(path, count=500):
    candidates = []
    locations = ["Pune", "Noida", "Delhi NCR", "Hyderabad", "Mumbai", "Bangalore", "Chennai", "New York"]
    job_titles = ["AI Engineer", "Software Engineer", "Data Scientist", "Backend Engineer", "ML Engineer"]
    industries = ["IT Services", "Product", "Consulting", "Finance"]
    company_sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"]

    for i in range(count):
        exp_years = round(random.uniform(1.0, 20.0), 1)
        location = random.choice(locations)
        title = random.choice(job_titles)
        industry = random.choice(industries)
        
        is_relevant = random.random() > 0.5
        keywords = "embedding vector retrieval LLM PyTorch" if is_relevant else "Java Spring SQL"
        
        candidate = {
            "candidate_id": f"CAND_{i:07d}",
            "profile": {
                "headline": f"{title} | {keywords}",
                "summary": f"Experienced {title} working on {keywords}.",
                "location": location,
                "country": "India" if location != "New York" else "USA",
                "years_of_experience": exp_years,
                "current_title": title,
                "current_company": "Tech Corp",
                "current_company_size": random.choice(company_sizes),
                "current_industry": industry
            },
            "career_history": [
                {
                    "company": "Tech Corp",
                    "title": title,
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "duration_months": 36,
                    "is_current": True,
                    "industry": industry,
                    "company_size": random.choice(company_sizes),
                    "description": f"Worked as {title} building {keywords}."
                }
            ],
            "education": [
                {
                    "institution": "Tech University",
                    "degree": "B.Tech",
                    "field_of_study": "Computer Science",
                    "start_year": 2015,
                    "end_year": 2019,
                    "grade": "A",
                    "tier": "tier_1" if random.random() > 0.7 else "tier_3"
                }
            ],
            "skills": [
                {
                    "name": kw,
                    "proficiency": "advanced",
                    "endorsements": random.randint(0, 20),
                    "duration_months": 24
                } for kw in keywords.split()
            ],
            "certifications": [
                {
                    "name": "Machine Learning",
                    "issuer": "Coursera",
                    "year": 2021
                }
            ] if random.random() > 0.5 else [],
            "redrob_signals": {
                "profile_completeness_score": random.randint(50, 100),
                "last_active_date": "2024-01-01T00:00:00Z", # assuming current time is later
                "open_to_work_flag": random.random() > 0.7,
                "recruiter_response_rate": random.random(),
                "avg_response_time_hours": random.randint(1, 48),
                "notice_period_days": random.choice([15, 30, 60, 90]),
                "github_activity_score": random.randint(-1, 100),
                "interview_completion_rate": random.random(),
                "offer_acceptance_rate": random.random(),
                "preferred_work_mode": random.choice(["hybrid", "onsite", "remote"]),
                "willing_to_relocate": random.random() > 0.5,
                "verified_email": True,
                "verified_phone": True,
                "expected_salary_range_inr_lpa": {
                    "min": random.randint(10, 30),
                    "max": random.randint(30, 60)
                }
            }
        }
        
        # Inject some honeypots
        if i == 10:
            candidate["career_history"][0]["duration_months"] = 120 # Mismatch with dates
        if i == 20:
            candidate["career_history"][0]["start_date"] = "1970-01-01" # Unrealistic start
        
        candidates.append(candidate)
        
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        for c in candidates:
            f.write(json.dumps(c) + '\n')

if __name__ == '__main__':
    generate_mock_data('data/candidates.jsonl.gz', 500)
    print("Mock data generated.")
