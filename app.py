import streamlit as st
import gzip
import json
import time
import pandas as pd
import tempfile
import os

from ranker.filter import filter_candidates
from ranker.embedder import compute_semantic_scores  
from ranker.scorer import rerank_candidates
from ranker.reasoner import generate_reasoning

st.set_page_config(page_title="ICD - Intelligent Candidate Discovery", layout="wide")

st.title("ICD — Intelligent Candidate Discovery")
st.subheader("Redrob Hackathon | Team HACK-X")

st.sidebar.header("Statistics")
stat_total = st.sidebar.empty()
stat_filtered = st.sidebar.empty()
stat_embedded = st.sidebar.empty()
stat_reranked = st.sidebar.empty()
stat_time = st.sidebar.empty()

uploaded_file = st.file_uploader("Upload candidates file (.jsonl or .jsonl.gz)", type=["jsonl", "gz"])

if st.button("Run Ranker"):
    if uploaded_file is None:
        st.warning("Please upload a file or it will run on the default data/candidates.jsonl.gz if exists.")
        file_path = 'data/candidates.jsonl.gz'
    else:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            file_path = tmp.name

    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        
        # Load
        status_text.text("Loading candidates...")
        candidates = []
        try:
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    candidates = [json.loads(line) for line in f if line.strip()]
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    candidates = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
            
        stat_total.metric("Total Candidates", len(candidates))
        progress_bar.progress(20)
        
        # Filter
        status_text.text("Stage 1: Filtering...")
        filtered = filter_candidates(candidates)
        stat_filtered.metric("Passed Filter", len(filtered))
        progress_bar.progress(40)
        
        # Embed
        status_text.text("Stage 2: Semantic Scoring...")
        top_300 = compute_semantic_scores(filtered, top_k=300)
        stat_embedded.metric("Embedded Top K", len(top_300))
        progress_bar.progress(60)
        
        # Score
        status_text.text("Stage 3: Reranking...")
        top_100 = rerank_candidates(top_300, top_k=100)
        stat_reranked.metric("Reranked Top K", len(top_100))
        progress_bar.progress(80)
        
        # Reason
        status_text.text("Stage 4: Generating Reasoning...")
        top_100 = generate_reasoning(top_100)
        progress_bar.progress(100)
        
        status_text.text("Done!")
        end_time = time.time()
        stat_time.metric("Time Taken (s)", f"{end_time - start_time:.2f}")
        
        rows = []
        for i, c in enumerate(top_100):
            rows.append({
                'candidate_id': c['candidate_id'],
                'rank': i + 1,
                'score': round(c.get('_final_score', 0.0), 6),
                'reasoning': c.get('_reasoning', '')
            })
            
        df = pd.DataFrame(rows)
        
        st.subheader("Top 20 Candidates")
        st.dataframe(df.head(20), use_container_width=True)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download full submission.csv",
            data=csv_data,
            file_name='submission.csv',
            mime='text/csv'
        )
