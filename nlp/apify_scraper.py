"""
Apify Google Reviews Scraper

Fetches Google Reviews for a given business using the Apify API.
Requires Apify API key and task ID.
"""

import requests
import json
from pathlib import Path
from typing import Optional, List, Dict


APIFY_BASE_URL = "https://api.apify.com/v2"
GOOGLE_REVIEWS_ACTOR_ID = "nwua9Oy5YvkQZ68dv"  # Google Reviews scraper actor


class ApifyGoogleReviewsScraper:
    """Scrape Google Reviews using Apify API."""
    
    def __init__(self, api_key: str):
        """Initialize with Apify API key.
        
        Args:
            api_key: Your Apify API key
        """
        self.api_key = api_key
        self.base_url = APIFY_BASE_URL
    
    def scrape_reviews(self, business_url: str, max_reviews: int = 100, sort_by: str = "newest") -> List[Dict]:
        """Scrape Google Reviews from a business URL.
        
        Args:
            business_url: Google Maps or Google Search business URL
            max_reviews: Maximum number of reviews to scrape (default: 100)
            sort_by: Sort order - "newest" or "most_relevant" (default: "newest")
        
        Returns:
            List of review dictionaries with keys: text, rating, reviewer_name, review_date
        """
        print(f"Starting Apify scraper for: {business_url}")
        
        # Prepare the actor input
        actor_input = {
            "startUrls": [{"url": business_url}],
            "maxReviews": max_reviews,
            "sortBy": sort_by,
            "language": "en"
        }
        
        # Run the actor
        run_response = self._run_actor(
            actor_id=GOOGLE_REVIEWS_ACTOR_ID,
            actor_input=actor_input
        )
        
        if not run_response or "data" not in run_response:
            print("Error: No data returned from Apify")
            return []
        
        # Extract reviews from the results
        reviews = self._extract_reviews(run_response["data"])
        print(f"Scraped {len(reviews)} reviews")
        return reviews
    
    def _run_actor(self, actor_id: str, actor_input: Dict) -> Optional[Dict]:
        """Run an Apify actor and get results.
        
        Args:
            actor_id: ID of the actor to run
            actor_input: Input configuration for the actor
        
        Returns:
            Response with results or None if failed
        """
        # Start the actor run
        url = f"{self.base_url}/acts/{actor_id}/runs"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        print(f"Starting actor run: {url}")
        response = requests.post(url, json=actor_input, headers=headers, timeout=30)
        
        if response.status_code != 201:
            print(f"Error starting actor: {response.status_code}")
            print(response.text)
            return None
        
        run_data = response.json()
        run_id = run_data.get("data", {}).get("id")
        
        if not run_id:
            print("Error: No run ID returned")
            return None
        
        print(f"Actor run started: {run_id}")
        
        # Wait for the run to complete and get results
        return self._get_run_results(run_id)
    
    def _get_run_results(self, run_id: str, max_wait_seconds: int = 300) -> Optional[Dict]:
        """Wait for actor run to complete and fetch results.
        
        Args:
            run_id: ID of the actor run
            max_wait_seconds: Maximum time to wait (default: 5 minutes)
        
        Returns:
            Results dataset or None if timed out
        """
        import time
        
        url = f"{self.base_url}/runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        elapsed = 0
        poll_interval = 5  # seconds
        
        while elapsed < max_wait_seconds:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Error fetching run status: {response.status_code}")
                return None
            
            run_data = response.json().get("data", {})
            status = run_data.get("status")
            
            print(f"Run status: {status} (elapsed: {elapsed}s)")
            
            if status == "SUCCEEDED":
                dataset_id = run_data.get("defaultDatasetId")
                return self._get_dataset(dataset_id)
            elif status in ["FAILED", "TIMED_OUT", "ABORTED"]:
                print(f"Actor run {status}")
                return None
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        print(f"Actor run timed out after {max_wait_seconds}s")
        return None
    
    def _get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Fetch results from an Apify dataset.
        
        Args:
            dataset_id: ID of the dataset
        
        Returns:
            Dictionary with 'data' key containing list of items
        """
        url = f"{self.base_url}/datasets/{dataset_id}/items"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        print(f"Fetching dataset: {dataset_id}")
        response = requests.get(url, headers=headers, timeout=30, params={"format": "json"})
        
        if response.status_code != 200:
            print(f"Error fetching dataset: {response.status_code}")
            return None
        
        items = response.json()
        print(f"Retrieved {len(items)} items from dataset")
        return {"data": items}
    
    def _extract_reviews(self, items: List[Dict]) -> List[Dict]:
        """Extract review text and metadata from Apify results.
        
        Args:
            items: List of items returned by Apify actor
        
        Returns:
            List of reviews with standardized keys
        """
        reviews = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Apify Google Reviews actor returns these fields
            review = {
                "text": item.get("reviewText") or item.get("text") or "",
                "rating": item.get("rating") or item.get("stars") or 5,
                "reviewer_name": item.get("reviewerName") or item.get("name") or "",
                "review_date": item.get("reviewDate") or item.get("publishedAtDate") or "",
            }
            
            # Only include non-empty reviews
            if review["text"].strip():
                reviews.append(review)
        
        return reviews
    
    def save_reviews_to_csv(self, reviews: List[Dict], output_path: str):
        """Save scraped reviews to CSV.
        
        Args:
            reviews: List of review dictionaries
            output_path: Path to save CSV file
        """
        import pandas as pd
        
        df = pd.DataFrame(reviews)
        df.rename(columns={
            "text": "Review",
            "reviewer_name": "Reviewer",
            "rating": "Rating"
        }, inplace=True)
        
        # Add sentiment column based on rating
        df["Sentiment"] = df["Rating"].apply(lambda r: "Positive" if r >= 4 else "Negative")
        
        df.to_csv(output_path, index=False)
        print(f"Saved {len(reviews)} reviews to {output_path}")


def scrape_and_save(business_url: str, api_key: str, output_path: str, max_reviews: int = 100):
    """Convenience function to scrape reviews and save to CSV.
    
    Args:
        business_url: Google Maps or Google Search business URL
        api_key: Apify API key
        output_path: Path to save reviews CSV
        max_reviews: Maximum reviews to scrape
    """
    scraper = ApifyGoogleReviewsScraper(api_key)
    reviews = scraper.scrape_reviews(business_url, max_reviews=max_reviews)
    
    if reviews:
        scraper.save_reviews_to_csv(reviews, output_path)
        return len(reviews)
    
    return 0
