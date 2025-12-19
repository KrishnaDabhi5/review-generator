# Review Generator

Lightweight, rule-based review generator using your `Restaurant reviews.csv` dataset.

## Setup
Create a virtual environment and install dependencies (Windows PowerShell):

```powershell
cd review-generator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m nltk.downloader punkt wordnet averaged_perceptron_tagger
python -m spacy download en_core_web_sm
```

Place your dataset at `review-generator/data/restaurant_reviews.csv`.

## Quick run (development)

Run the API from the `review-generator` folder (PowerShell):

```powershell
cd review-generator
uvicorn api.main:app --reload --port 8000
```

Example request (curl):

```bash
curl -X POST "http://127.0.0.1:8000/generate-review" \
	-H "Content-Type: application/json" \
	-d '{"business":"Beyond Flavours","level":"medium"}'
```

PowerShell example:

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/generate-review" \
	-ContentType "application/json" -Body '{"business":"Beyond Flavours","level":"medium"}'
```

## Notes & Recommendations

- The API currently reads the CSV and builds sentence buckets on each request — fine for prototyping. For production, precompute and persist buckets (JSON/pickle) and load them at startup.
- The generator is intentionally rule-based to avoid heavy ML models and to stay fast and lightweight.
- Ensure `Restaurant reviews.csv` has a `Review` column (case-sensitive) or adjust `api/main.py` to your column name.

If you want, I can add a small script that precomputes buckets and saves them to `data/buckets.json` so the API starts instantly.
You can precompute buckets (recommended for faster startup):

```powershell
cd review-generator
python nlp/precompute_buckets.py --csv data/restaurant_reviews.csv --out data/buckets.json
```

If `data/buckets.json` exists the API will load it at startup instead of rebuilding buckets on every request.
