# Review Generator — Project Resource Document

Project Name: Review Generator (Python-Based NLP System)

## 1. Dataset Analysis (Your Actual Dataset)

- Dataset Name: `Restaurant reviews.csv`
- Size: Rows: 10,000 reviews | Columns: 8

Columns Breakdown

| Column | Use in Project | Action |
|---|---:|:---|
| Restaurant | Business name | KEEP |
| Reviewer | User name | DROP |
| Review | Review text | CORE |
| Rating | Star rating | OPTIONAL |
| Metadata | Reviewer stats | DROP |
| Time | Review time | DROP |
| Pictures | Image count | DROP |
| 7514 | Corrupted column | DROP |

## 2. What This Dataset Is Perfect For

This dataset already contains:

- Natural human reviews
- Simple English sentences
- Real Google-style tone
- Positive sentiment (mostly 4–5⭐)

This makes it ideal for review text generation. You do NOT need deep learning immediately.

## 3. Final Clean Dataset Structure

After cleaning the dataset should have:

Restaurant | Review | Rating

Only `Review` is required for NLP generation.

## 4. Project Objective (Re-defined)

Build a Python NLP-based review generator that:

- Generates unique Google-style reviews
- Uses difficulty levels
- Avoids duplicates
- Is fast and lightweight
- Works without heavy ML models

## 5. Overall Architecture (Python Only)

CSV Dataset
   ↓
Text Cleaning
   ↓
Sentence Extraction
   ↓
Sentence Buckets
   ↓
Randomized Review Generator
   ↓
Difficulty Controller
   ↓
Web API (FastAPI)

## 6. Data Preprocessing (Python)

Required Libraries:
- pandas
- re
- nltk
- spacy
- scikit-learn

Cleaning Steps:
- Remove reviewer names
- Remove emojis & special characters
- Convert to lowercase
- Remove very short reviews (<5 words)
- Sentence tokenize reviews

## 7. NLP Analysis on Dataset

What We Extract From Reviews:

- Sentence Types
  - Opening experience sentences
  - Service quality sentences
  - Ambience sentences
  - Staff behavior sentences
  - Closing recommendation sentences

## 8. Sentence Bucketing (CORE LOGIC)

Create sentence buckets from your own dataset. Example Buckets (Auto-Generated):

- Opening
  - great experience at this place
  - wonderful ambience and food
  - very pleasant dining experience

- Service
  - staff was very polite
  - service was quick and professional
  - staff was helpful and friendly

- Food / Quality
  - food was delicious
  - quality was excellent
  - taste was amazing

- Closing
  - highly recommended
  - will visit again
  - must try place

Each sentence comes directly from your dataset.

## 9. Review Generation Logic (Important)

Randomized Review Builder (example):

review = (
  random.choice(opening) +
  random.choice(service) +
  random.choice(food) +
  random.choice(closing)
)

Apply:
- Random order
- Optional sentence skip
- Synonym swap

This ensures no duplicate reviews.

## 10. Difficulty Level Logic

Level | Sentences Used
---|---
Easy | 2
Medium | 4
Detailed | 6

## 11. Ensuring Uniqueness (Critical)

Techniques Used:
- Random sentence selection
- Random sentence order
- Synonym replacement (WordNet)
- Sentence dropping

Target duplicate chance: <0.5%

## 12. ML / DL Decision (Very Important)

Do you need Deep Learning?

❌ No, not now

Why?
- Dataset size is small (10k)
- Reviews are repetitive
- Rule-based NLP is safer for Google
- Faster development

## 13. OPTIONAL: ML Enhancement (Later)

If you want ML:
- Use TF-IDF + sentence clustering (NOT neural networks)

Purpose:
- Better sentence grouping
- Tone consistency

## 14. Python Tech Stack

Backend:
- Python
- FastAPI
- pandas
- nltk / spacy

NLP:
- Sentence tokenization
- N-grams
- WordNet synonyms

## 15. Web Integration (Later)

Expose an endpoint `POST /generate-review`

Input example:

{
  "business": "Beyond Flavours",
  "level": "medium"
}

Output example:

{
  "review": "I had a very pleasant experience..."
}

## 16. Google Safety Rules (Must Follow)

- Never repeat exact reviews
- No keyword stuffing
- Natural tone only
- Max 1 review per user

## 17. Project Folder Structure (Recommended)

review-generator/
│
├── data/
│   └── restaurant_reviews.csv
│
├── nlp/
│   ├── preprocess.py
│   ├── sentence_extractor.py
│   ├── generator.py
│
├── api/
│   └── main.py
│
└── requirements.txt

## 18. What This Project Demonstrates (For Resume)

- NLP preprocessing
- Real dataset analysis
- Text generation logic
- Product-oriented AI thinking
- Google-safe content generation

## 19. Final Recommendation

Best Approach for You:

- ✅ Rule-based NLP generator
- ✅ Python only
- ✅ Dataset-driven sentences

---

Notes:
- The original dataset file `Restaurant reviews.csv` is present in the workspace root; move or copy it to `review-generator/data/restaurant_reviews.csv` when ready.
- Next steps: implement `nlp/preprocess.py` and `nlp/generator.py`, then add a FastAPI wrapper in `api/main.py`.
