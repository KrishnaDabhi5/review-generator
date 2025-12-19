#!/usr/bin/env python3
"""
Scrape Google Reviews using Apify and precompute buckets.

Usage:
    python tools/scrape_and_precompute.py --url "https://www.google.com/maps/place/YOUR_BUSINESS" \
                                          --api-key "your_apify_key" \
                                          --max-reviews 200
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'nlp'))

from apify_scraper import scrape_and_save
import precompute_buckets as pb
from preprocess import load_dataset, preprocess_dataframe


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Reviews and precompute buckets")
    parser.add_argument("--url", required=True, help="Google Maps or Search business URL")
    parser.add_argument("--api-key", required=True, help="Apify API key")
    parser.add_argument("--max-reviews", type=int, default=200, help="Max reviews to scrape (default: 200)")
    parser.add_argument("--output-csv", default="data/scraped_reviews.csv", help="Path to save scraped reviews CSV")
    parser.add_argument("--output-buckets", default="data/buckets.json", help="Path to save computed buckets")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("STEP 1: Scraping Google Reviews with Apify")
    print("=" * 70)
    
    count = scrape_and_save(args.url, args.api_key, args.output_csv, max_reviews=args.max_reviews)
    
    if count == 0:
        print("ERROR: No reviews scraped. Check URL and API key.")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("STEP 2: Preprocessing and Bucketing")
    print("=" * 70)
    
    # Load and preprocess
    df = load_dataset(args.output_csv)
    print(f"Loaded {len(df)} reviews from {args.output_csv}")
    
    # Determine which column to use for filtering
    if "Sentiment" in df.columns:
        df_filtered = preprocess_dataframe(df, review_col="Review", sentiment_col="Sentiment")
        print(f"Filtered to {len(df_filtered)} positive reviews (by Sentiment column)")
    elif "Rating" in df.columns:
        df_filtered = preprocess_dataframe(df, review_col="Review", rating_col="Rating", min_rating=4)
        print(f"Filtered to {len(df_filtered)} positive reviews (rating >= 4)")
    else:
        df_filtered = preprocess_dataframe(df, review_col="Review")
        print(f"Cleaned {len(df_filtered)} reviews")
    
    # Build buckets
    buckets = pb.build_buckets(df_filtered)
    
    print("\nBucket Summary:")
    for k, v in buckets.items():
        print(f"  {k:12s}: {len(v):6d} sentences")
    
    # Save buckets
    import json
    Path(args.output_buckets).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_buckets, 'w', encoding='utf-8') as f:
        json.dump(buckets, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved buckets to: {args.output_buckets}")
    print("\n✓ Done! The API will use the new buckets on next reload.")


if __name__ == "__main__":
    main()
