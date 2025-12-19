import os
import pandas as pd
from nlp.preprocess import preprocess_dataframe, clean_text
from nlp.sentence_extractor import bucket_sentences, extract_sentences
import json

def load_and_preprocess_both_datasets():
    """
    Load both European Restaurant Reviews and Restaurant reviews CSVs.
    Preprocess and combine them.
    """
    data_dir = "data"
    
    # Load European Restaurant Reviews
    european_path = os.path.join(data_dir, "European Restaurant Reviews.csv")
    restaurant_path = os.path.join(data_dir, "Restaurant reviews.csv")
    
    print("=" * 70)
    print("LOADING AND PREPROCESSING BOTH DATASETS")
    print("=" * 70)
    
    all_reviews = []
    
    # Load European Restaurant Reviews
    if os.path.exists(european_path):
        print(f"\n[1/2] Loading European Restaurant Reviews...")
        df_european = pd.read_csv(european_path)
        print(f"  Shape: {df_european.shape}")
        print(f"  Columns: {list(df_european.columns)}")
        
        # Preprocess with Sentiment column
        df_european_clean = preprocess_dataframe(
            df_european,
            review_col="Reviews",
            sentiment_col="Sentiment",
            rating_col=None,
            min_rating=4
        )
        print(f"  After filtering: {len(df_european_clean)} reviews")
        
        # Extract reviews as list
        reviews_european = df_european_clean["Review"].tolist()
        all_reviews.extend(reviews_european)
        print(f"  Added {len(reviews_european)} reviews from European dataset")
    else:
        print(f"  ERROR: {european_path} not found")
    
    # Load Restaurant reviews
    if os.path.exists(restaurant_path):
        print(f"\n[2/2] Loading Restaurant Reviews...")
        df_restaurant = pd.read_csv(restaurant_path)
        print(f"  Shape: {df_restaurant.shape}")
        print(f"  Columns: {list(df_restaurant.columns)}")
        
        # Preprocess with Rating column
        df_restaurant_clean = preprocess_dataframe(
            df_restaurant,
            review_col="Review",
            sentiment_col=None,
            rating_col="Rating",
            min_rating=4
        )
        print(f"  After filtering: {len(df_restaurant_clean)} reviews")
        
        # Extract reviews as list
        reviews_restaurant = df_restaurant_clean["Review"].tolist()
        all_reviews.extend(reviews_restaurant)
        print(f"  Added {len(reviews_restaurant)} reviews from Restaurant dataset")
    else:
        print(f"  ERROR: {restaurant_path} not found")
    
    print(f"\n{'=' * 70}")
    print(f"TOTAL REVIEWS COMBINED: {len(all_reviews)}")
    print(f"{'=' * 70}")
    
    return all_reviews

def build_buckets_from_reviews(reviews):
    """
    Extract sentences from reviews and bucket them by category.
    """
    print(f"\n[3/3] Extracting and bucketing sentences...")
    
    all_sentences = []
    
    for i, review in enumerate(reviews):
        if pd.isna(review):
            continue
        
        try:
            sentences = extract_sentences(str(review))
            all_sentences.extend(sentences)
        except Exception as e:
            print(f"  Warning: Could not extract sentences from review {i}: {e}")
            continue
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1} reviews...")
    
    print(f"  Total sentences extracted: {len(all_sentences)}")
    
    # Bucket sentences
    buckets = bucket_sentences(all_sentences)
    
    print(f"\nBucket Statistics:")
    for category, sentences in buckets.items():
        print(f"  {category}: {len(sentences)} sentences")
    
    return buckets

def save_buckets_to_json(buckets, output_path="data/buckets.json"):
    """Save buckets to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(buckets, f, ensure_ascii=False, indent=2)
    print(f"\nBuckets saved to {output_path}")

if __name__ == "__main__":
    # Load and preprocess both datasets
    reviews = load_and_preprocess_both_datasets()
    
    # Build buckets
    buckets = build_buckets_from_reviews(reviews)
    
    # Save buckets
    save_buckets_to_json(buckets)
    
    print(f"\n{'=' * 70}")
    print("PREPROCESSING COMPLETE!")
    print(f"{'=' * 70}")
    print(f"\nYou now have:")
    print(f"  - {len(reviews)} combined reviews from both datasets")
    print(f"  - {sum(len(s) for s in buckets.values())} sentences bucketed")
    print(f"  - Ready for template-based review generation")
