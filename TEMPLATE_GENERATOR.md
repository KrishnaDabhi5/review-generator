# Template-Based Review Generator

## Overview

The review generator now uses a **hybrid template + dataset approach** that combines:

1. **Predefined Templates** (`templates.json`) - Professional templates for opening, food, service, ambience, closing
2. **Dataset Sentences** (`buckets.json`) - Real sentences extracted from 6,562+ reviews

This approach provides:
- ✅ More variety and less repetition
- ✅ Natural, professional review tone
- ✅ Fast generation (no ML/DL)
- ✅ Lightweight system
- ✅ Easy customization

## Datasets Combined

| Dataset | Reviews | Status |
|---------|---------|--------|
| European Restaurant Reviews | 1,237 | Sentiment = "Positive" |
| Restaurant Reviews | 5,325 | Rating ≥ 4 |
| **Total** | **6,562** | **Combined** |

## Sentence Buckets

Extracted from combined datasets:

| Category | Sentences | Purpose |
|----------|-----------|---------|
| Opening | 2,188 | First impression, introduction |
| Service | 3,862 | Staff, attentiveness, professionalism |
| Food | 16,442 | Taste, quality, menu variety |
| Ambience | 1,480 | Atmosphere, cleanliness, decor |
| Closing | 5,420 | Recommendation, return intent |
| **Total** | **29,392** | **For generation** |

## Generation Levels

### Easy (2 sentences)
- 1 opening template
- 1 food or service sentence from dataset

**Example:**
> "I had a great experience at Rati Kaka Ni Bhajipav. The food was absolutely delicious!"

### Medium (4 sentences)
- 1 opening template
- 1 food (60% template, 40% dataset)
- 1 service/staff (50/50 mix)
- 1 closing template

**Example:**
> "I recently visited Rati Kaka Ni Bhajipav and was very impressed. The food was absolutely delicious! Staff were very polite and attentive. I would definitely visit again soon."

### Detailed (6+ sentences)
- 1 opening template
- 1 environment/ambience sentence
- 1 food sentence
- 1 service/staff sentence
- 1 value/pricing template
- 1 closing template

**Example:**
> "My visit to Rati Kaka Ni Bhajipav was wonderful. The atmosphere was comfortable and welcoming. Everything we tasted was flavorful and fresh. The staff went above and beyond to help us. Fair pricing and excellent value. I highly recommend them to everyone."

## Template Structure

```json
{
  "opening": [5 templates with {business_name} placeholder],
  "food": [5 templates],
  "staff_specific": [5 templates],
  "speed": [5 templates],
  "value": [5 templates],
  "service": [5 templates],
  "environment": [5 templates],
  "closing": [5 templates]
}
```

## Variety Features

1. **Random Template Selection** - 5 templates per category, randomly chosen
2. **Mixed Sources** - Templates + dataset sentences = higher variety
3. **Multiple Datasets** - 6,562 reviews means diverse sentence pool
4. **Category Distribution** - 16K food sentences, 5.4K closing, 3.8K service, etc.
5. **Smart Ordering** - Sentences flow naturally: opening → details → closing

## Usage

### Generate via Web Form
```
GET http://127.0.0.1:8001/test
```

### Generate via API
```bash
curl -X POST http://127.0.0.1:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business": "Rati Kaka Ni Bhajipav", "level": "medium"}'
```

### Generate via Python
```python
from nlp.template_generator import TemplateReviewGenerator

gen = TemplateReviewGenerator('data/templates.json', 'data/buckets.json')

# Easy review
review = gen.generate_review('Your Business', 'easy')

# Medium review (default)
review = gen.generate_review('Your Business', 'medium')

# Detailed review
review = gen.generate_review('Your Business', 'detailed')
```

## Benefits Over Pure Bucketing

| Aspect | Old Bucketing | New Templates |
|--------|---------------|---------------|
| Variety | 5,000 sentences per category | 5 templates + 29K sentences |
| Flow | Random order | Structured (opening → closing) |
| Professionalism | Variable tone | Consistent quality |
| Repetition | Higher | Much lower |
| Customization | Hard | Easy (edit templates.json) |

## Regenerating Buckets

If you have new CSV data, regenerate buckets:

```bash
python tools/preprocess_both_datasets.py
```

This will:
1. Load both CSV files
2. Filter by sentiment/rating
3. Extract and bucket sentences
4. Save to `data/buckets.json`
5. API auto-reloads with new data

## File Locations

- **Templates:** `data/templates.json`
- **Buckets:** `data/buckets.json`
- **Generator Code:** `nlp/template_generator.py`
- **Precompute Tool:** `tools/preprocess_both_datasets.py`

## Performance

- **Generation Speed:** <100ms per review (no ML, pure template mixing)
- **Memory Usage:** ~50MB (all templates + buckets in RAM)
- **Scalability:** Add more templates/sentences = instant variety increase
