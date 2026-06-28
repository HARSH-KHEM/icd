# ICD (Intelligent Candidate Discovery)

Redrob AI × Hack2skill (Track 1 - Data & AI Challenge)

## Architecture

This project implements a 4-stage ranking pipeline:
1. **Filtering**: Rule-based filtering (Honeypot detection, Experience constraints, Domain relevance, Pure services disqualification).
2. **Semantic Scoring**: Uses `all-MiniLM-L6-v2` to compute cosine similarity between candidate profiles and the Job Description.
3. **Multi-signal Reranking**: Computes a final score using semantic score, experience, behavioral signals, and context.
4. **Reasoning Generation**: Generates a brief explanation based on candidate profile facts.

## Setup

```bash
pip install -r requirements.txt
```

## Run Ranking

```bash
python rank.py --candidates ./data/candidates.jsonl.gz --out ./submission.csv
```
Expected runtime: ~2-3 minutes on CPU

## Streamlit App

```bash
streamlit run app.py
```
