import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'nlp'))

import precompute_buckets as pb
from preprocess import load_dataset, preprocess_dataframe

csv_path = r'c:\wakanda\ironman\review-generator\data\European Restaurant Reviews.csv'
print('CSV path:', csv_path)

df = load_dataset(csv_path)
print('Loaded df shape:', df.shape)
print('Columns:', list(df.columns))
print('Sample Sentiment values:', df['Sentiment'].unique() if 'Sentiment' in df.columns else 'No Sentiment column')

df2 = preprocess_dataframe(df, review_col='Review', sentiment_col='Sentiment')
print('After preprocess shape:', df2.shape)

buckets = pb.build_buckets(df2)
print('Buckets keys:', list(buckets.keys()))
for k,v in buckets.items():
    print(f'  {k:12s}: {len(v):6d} sentences')

out = r'c:\wakanda\ironman\review-generator\data\buckets.json'
import json
with open(out,'w',encoding='utf-8') as f:
    json.dump(buckets,f,ensure_ascii=False,indent=2)
print('Wrote', out)
