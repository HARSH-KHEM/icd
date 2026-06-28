from sentence_transformers import SentenceTransformer, util
import os

def compute_semantic_scores(candidates: list, top_k: int = 300) -> list:
    if not candidates:
        return []
        
    os.makedirs('models', exist_ok=True)
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')
    
    jd_text = """Senior AI Engineer role requiring production experience with embeddings-based retrieval systems, 
vector databases (FAISS, Pinecone, Weaviate, Qdrant, Elasticsearch), strong Python, 
evaluation frameworks for ranking systems (NDCG, MRR, MAP). 
Ideal: 6-8 years at product companies, shipped end-to-end ranking or search or recommendation systems, 
hybrid retrieval, LLM integration, fine-tuning experience. 
Located in Pune, Noida, Delhi NCR, Hyderabad, Mumbai, Bangalore. 
NOT: pure services background, research-only roles, CV/speech/robotics specialists, 
consulting firms only (TCS, Infosys, Wipro, Accenture, Cognizant)."""

    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    
    candidate_texts = []
    for c in candidates:
        parts = []
        parts.append(c.get('profile', {}).get('headline', ''))
        parts.append(c.get('profile', {}).get('summary', ''))
        
        for job in c.get('career_history', []):
            parts.append(job.get('description', ''))
            
        skills_str = " ".join([f"{s.get('name')} {s.get('proficiency')}" for s in c.get('skills', [])])
        parts.append(skills_str)
        
        parts.append(c.get('profile', {}).get('current_title', ''))
        
        candidate_texts.append(" ".join(filter(None, parts)))
        
    batch_size = 64
    embeddings = model.encode(candidate_texts, batch_size=batch_size, convert_to_tensor=True)
    
    cosine_scores = util.cos_sim(jd_embedding, embeddings)[0]
    
    for i, score in enumerate(cosine_scores):
        candidates[i]['_semantic_score'] = score.item()
        
    candidates.sort(key=lambda x: x['_semantic_score'], reverse=True)
    return candidates[:top_k]
