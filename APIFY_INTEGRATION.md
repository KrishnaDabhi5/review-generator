# Apify Google Reviews Integration

This module allows you to scrape Google Reviews directly from a business using the **Apify API**.

## Setup

### 1. Install Apify Package

```powershell
pip install requests
```

### 2. Get Your Apify API Key

1. Sign up at [Apify Console](https://console.apify.com/)
2. Go to **Settings → Integrations** to get your API key
3. You already have: `cQifyvPLDJs1kbMKZv2W6BtS0zYqSl2q5akU`

### 3. Find Business URL

Get the Google Maps or Google Search URL for your target business. Example:
- Google Maps: `https://www.google.com/maps/place/BUSINESS+NAME/@COORDINATES`
- Google Search: `https://www.google.com/search?q=BUSINESS+NAME`

## Usage

### Quick Scrape & Precompute

```powershell
cd review-generator
python tools/scrape_and_precompute.py `
  --url "https://www.google.com/maps/place/Beyond+Flavours" `
  --api-key "cQifyvPLDJs1kbMKZv2W6BtS0zYqSl2q5akU" `
  --max-reviews 200
```

This will:
1. Scrape up to 200 Google Reviews
2. Save to `data/scraped_reviews.csv`
3. Filter to positive reviews only
4. Precompute `data/buckets.json`
5. API will auto-reload with new reviews

### Python API

```python
from nlp.apify_scraper import scrape_and_save

# Scrape and save to CSV
count = scrape_and_save(
    business_url="https://www.google.com/maps/place/Beyond+Flavours",
    api_key="cQifyvPLDJs1kbMKZv2W6BtS0zYqSl2q5akU",
    output_path="data/my_reviews.csv",
    max_reviews=100
)
print(f"Scraped {count} reviews")
```

## Output Format

Scraped reviews are saved as CSV with columns:
- **Review** — Review text
- **Reviewer** — Reviewer name
- **Rating** — Star rating (1-5)
- **Sentiment** — "Positive" (rating ≥ 4) or "Negative"
- **review_date** — Date review was posted

## How It Works

1. **Apify Actor** — Uses Google Reviews scraper actor (ID: `nwua9Oy5YvkQZ68dv`)
2. **API Call** — Sends scraping request to Apify
3. **Wait & Poll** — Polls for completion (typically 2-5 minutes)
4. **Dataset Fetch** — Downloads results from Apify dataset
5. **Preprocessing** — Cleans, filters, and buckets sentences
6. **Bucket Save** — Exports to `buckets.json` for API use

## Limitations & Notes

- **First Run** — May take 2-5 minutes to complete
- **Rate Limits** — Apify has limits; check your plan
- **Manual Reviews Only** — Google blocks automated scraping; Apify handles this legally
- **Sentiment Auto-Detection** — Based on star rating (4-5★ = Positive)
- **Updates** — Re-run the script anytime to refresh reviews

## Example Workflow

```powershell
# 1. Scrape restaurant reviews
python tools/scrape_and_precompute.py `
  --url "https://www.google.com/maps/place/La+Bella+Restaurant" `
  --api-key "cQifyvPLDJs1kbMKZv2W6BtS0zYqSl2q5akU" `
  --max-reviews 150

# 2. Check the new buckets were created
ls data/buckets.json

# 3. Visit http://127.0.0.1:8001/test and generate reviews!
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authorization failed" | Check API key is correct |
| "No data returned" | Verify business URL is accessible on Google |
| "Timed out" | Increase `--max-reviews` timeout or try smaller max |
| Script hangs | Apify may be rate-limited; wait and retry |

## Next Steps

After scraping, the generator will:
- **Extract sentences** from reviews
- **Categorize** into opening/service/food/ambience/closing
- **Generate unique reviews** by combining sentences
- **Replace names** with the business name entered in the form
- **Apply synonyms** for variation

All powered by real Google Reviews data!
