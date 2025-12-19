#!/usr/bin/env python3
"""Quick test of the refined generator logic."""

import sys
from pathlib import Path

# Add nlp to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "nlp"))

from sentence_extractor import bucket_sentences, extract_sentences
from generator import generate_review

# Sample test data
test_reviews = [
    "Great experience at this place. The staff was very polite and helpful. Food was delicious and well prepared. Highly recommended!",
    "Wonderful ambience and food. Service was quick and professional. Must try their pasta. Will visit again soon.",
    "Pleasant dining experience. The atmosphere was cozy and comfortable. Dishes were excellent. Definitely coming back!",
    "Amazing spot with friendly staff. Quality of food is outstanding. Beautiful decor. You should definitely visit.",
    "Love this restaurant. Excellent service and tasty food. Music was nice. Best place in town!",
]

# Extract and bucket sentences
print("=" * 70)
print("Testing sentence extraction and bucketing...")
print("=" * 70)

all_buckets = {"opening": [], "service": [], "food": [], "ambience": [], "closing": []}

for review in test_reviews:
    sentences = extract_sentences(review)
    print(f"\nOriginal: {review}\nSentences: {len(sentences)}")
    
    buckets = bucket_sentences(sentences)
    for bucket_name, bucket_sents in buckets.items():
        if bucket_sents:
            print(f"  {bucket_name:10s}: {len(bucket_sents):2d} - {bucket_sents[0][:50]}...")
            all_buckets[bucket_name].extend(bucket_sents)

# Test generation at different difficulty levels
print("\n" + "=" * 70)
print("Testing review generation...")
print("=" * 70)

levels = ["easy", "medium", "detailed"]
for level in levels:
    print(f"\n[{level.upper()}]")
    for i in range(3):
        review = generate_review(all_buckets, level=level)
        print(f"  {i+1}. {review}")

print("\n" + "=" * 70)
print("✓ Generator test complete!")
print("=" * 70)
