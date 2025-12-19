import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'nlp'))
from preprocess import load_dataset, preprocess_dataframe
from sentence_extractor import extract_sentences, bucket_sentences

csv_path = Path('data') / 'Restaurant reviews.csv'
out_path = Path('data') / 'buckets.json'
print('CSV:', csv_path.resolve())
if not csv_path.exists():
    print('CSV not found')
    raise SystemExit(1)

df = load_dataset(csv_path)
print('Loaded rows:', len(df))
df = preprocess_dataframe(df, review_col='Review')
print('After preprocess rows:', len(df))

buckets = {"opening": [], "service": [], "food": [], "ambience": [], "closing": []}
count = 0
for r in df['Review'].astype(str).tolist():
    sents = extract_sentences(r)
    b = bucket_sentences(sents)
    for k, v in b.items():
        buckets[k].extend(v)
    count += 1
    if count % 1000 == 0:
        print('Processed', count)

for k in list(buckets.keys()):
    # deduplicate and strip
    seen = set()
    out = []
    for s in buckets[k]:
        s2 = s.strip()
        if s2 and s2 not in seen:
            seen.add(s2)
            out.append(s2)
    buckets[k] = out
    print(k, 'count ->', len(buckets[k]))

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(buckets, f, ensure_ascii=False, indent=2)
print('Wrote', out_path.resolve())
