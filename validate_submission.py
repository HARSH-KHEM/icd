import sys
import pandas as pd

def validate(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        return False
        
    if len(df) != 100:
        print(f"Expected 100 rows, got {len(df)}", file=sys.stderr)
        return False
        
    expected_cols = ['candidate_id', 'rank', 'score', 'reasoning']
    if list(df.columns) != expected_cols:
        print(f"Expected columns {expected_cols}, got {list(df.columns)}", file=sys.stderr)
        return False
        
    ranks = df['rank'].tolist()
    if sorted(ranks) != list(range(1, 101)):
        print("Ranks must be exactly 1 to 100, each appearing once", file=sys.stderr)
        return False
        
    scores = df['score'].tolist()
    for i in range(1, len(scores)):
        if scores[i] > scores[i-1]:
            print("Scores must be monotonically non-increasing", file=sys.stderr)
            return False
            
    print("Validation passed!")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_submission.py <path_to_csv>", file=sys.stderr)
        sys.exit(1)
    
    if not validate(sys.argv[1]):
        sys.exit(1)
    sys.exit(0)
