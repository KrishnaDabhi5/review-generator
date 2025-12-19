import json
from pathlib import Path
from collections import defaultdict
import argparse

from preprocess import load_dataset, preprocess_dataframe
from sentence_extractor import extract_sentences, bucket_sentences


def build_buckets(df):
    buckets = defaultdict(list)
    for r in df["Review"].astype(str).tolist():
        sents = extract_sentences(r)
        b = bucket_sentences(sents)
        for k, v in b.items():
            buckets[k].extend(v)
    # deduplicate and strip
    out = {k: list({s.strip(): None for s in v}.keys()) for k, v in buckets.items()}
    return out


def main(csv_path: str, out_path: str):
    csv = Path(csv_path)
    out = Path(out_path)
    if not csv.exists():
        raise SystemExit(f"CSV not found: {csv}")
    df = load_dataset(csv)
    df = preprocess_dataframe(df, review_col="Review")
    buckets = build_buckets(df)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(buckets, f, ensure_ascii=False, indent=2)
    print(f"Wrote buckets to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/Restaurant_reviews.csv")
    ap.add_argument("--out", default="data/buckets.json")
    args = ap.parse_args()
    main(args.csv, args.out)
