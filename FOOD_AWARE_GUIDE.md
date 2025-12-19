# 🍽️ Food-Aware Review Generation

## Overview

You now have a **food-aware review generation system** that:

✅ **Detects food names** from restaurant menus (pongal, cacio a pepe, ghobi manchurian, etc.)
✅ **Stores food items** for each restaurant in a database
✅ **Generates reviews** mentioning specific dishes from the menu
✅ **Different reviews per restaurant** based on actual menu items
✅ **Supports OCR preprocessing** for image-based menu processing
✅ **Extractable from menu text** or manually added

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│         MENU PROCESSING PIPELINE                         │
└──────────────────────────────────────────────────────────┘
                        ↓
    ┌──────────────────┬──────────────────┐
    ↓                  ↓                  ↓
[Menu Image]    [Menu Text]        [Manual Entry]
  (OCR)         (Extract)          (Add API)
    ↓                  ↓                  ↓
    └──────────────────┬──────────────────┘
                       ↓
            ┌──────────────────────┐
            │ FoodItemExtractor    │
            │ - Extract food names │
            │ - Fuzzy matching     │
            │ - OCR error handling │
            └──────────────────────┘
                       ↓
            ┌──────────────────────┐
            │ Food Database        │
            │ data/food_items.json │
            │ Per-restaurant menus │
            └──────────────────────┘
                       ↓
        ┌─────────────────────────────┐
        │ FoodAwareReviewGenerator    │
        │ - Templates + food names    │
        │ - Mentions specific dishes  │
        │ - 3 difficulty levels       │
        └─────────────────────────────┘
                       ↓
            ┌──────────────────────┐
            │ Generated Reviews    │
            │ With food mentions   │
            │ "...loved the biryani│
            │  ...their pongal..." │
            └──────────────────────┘
```

---

## Files Created

### Core Components

**`nlp/food_extractor.py`** (280 lines)
- `FoodItemExtractor` class
- Extract food items from text
- Fuzzy matching for OCR errors
- Manage per-restaurant food databases
- Get/set/query food items

**`nlp/food_aware_generator.py`** (280 lines)
- `FoodAwareReviewGenerator` class
- Generate reviews mentioning specific foods
- Food-specific sentence templates:
  - Praise: "The {food} was absolutely delicious!"
  - Recommend: "Highly recommend trying the {food}."
  - Portion: "The {food} portions are generous."
- 3 difficulty levels with food integration

**`api/main.py`** (Updated)
- New endpoints for food management
- Enhanced request models
- Integration with both generators

**`demo_food_aware.py`**
- Live demonstration of food-aware generation
- Shows multiple restaurants
- Displays database statistics

---

## API Endpoints

### 1. **Add Restaurant Menu**
```bash
POST /api/add-menu
{
  "restaurant": "Rati Kaka Ni Bhajipav",
  "food_items": ["pongal", "dosa", "idly", "samosa", "biryani"]
}
```

**Response:**
```json
{
  "message": "Added 5 food items for Rati Kaka Ni Bhajipav",
  "restaurant": "Rati Kaka Ni Bhajipav",
  "food_items": ["pongal", "dosa", "idly", "samosa", "biryani"]
}
```

### 2. **Extract Foods from Menu Text**
```bash
POST /api/extract-foods
{
  "menu_text": "Our specialties: Pongal, Dosa, Idly, Samosa, Biryani, Curry, Naan",
  "cuisine_type": "indian"  # Optional
}
```

**Response:**
```json
{
  "detected_foods": ["pongal", "dosa", "idly", "samosa", "biryani", "curry", "naan"],
  "total": 7,
  "menu_text_snippet": "Our specialties: Pongal, Dosa, Idly..."
}
```

### 3. **Generate Review with Food Items**
```bash
POST /api/generate-with-food
{
  "business": "Rati Kaka Ni Bhajipav",
  "level": "medium",
  "food_items": ["pongal", "dosa", "samosa"]  # Optional (uses stored menu if not provided)
}
```

**Response:**
```json
{
  "review": "My visit to Rati Kaka Ni Bhajipav was wonderful. The pongal was absolutely delicious! Staff were very polite and attentive. Highly recommend trying the samosa."
}
```

### 4. **Get Restaurant's Menu Items**
```bash
GET /api/restaurant-foods/rati-kaka-ni-bhajipav
```

**Response:**
```json
{
  "restaurant": "rati-kaka-ni-bhajipav",
  "food_items": ["pongal", "dosa", "idly", "samosa", "biryani"],
  "total": 5
}
```

### 5. **Get All Restaurants**
```bash
GET /api/all-restaurants
```

**Response:**
```json
{
  "restaurants": ["rati-kaka-ni-bhajipav", "trattoria-roma", "golden-dragon"],
  "total_restaurants": 3,
  "stats": {
    "total_restaurants": 3,
    "total_unique_foods": 18,
    "average_items_per_restaurant": 6.0
  }
}
```

---

## How It Works

### Step 1: Add Restaurant Menu
```python
from nlp.food_extractor import FoodItemExtractor

extractor = FoodItemExtractor('data/food_items.json')

# Add menu items for a restaurant
foods = ['pongal', 'dosa', 'idly', 'samosa', 'biryani']
extractor.add_restaurant_foods("Rati Kaka Ni Bhajipav", foods)
```

### Step 2: Extract Foods from Menu Text
```python
# If you have menu text (from OCR or manual)
menu_text = "Our specialties: Pongal, Dosa, Idly, Samosa, Biryani"
detected = extractor.extract_from_text(menu_text)
print(detected)  # ['pongal', 'dosa', 'idly', 'samosa', 'biryani']

# With OCR (handles errors like "lndian" instead of "indian")
detected = extractor.extract_from_ocr_text(ocr_text, cuisine_type="indian")
```

### Step 3: Generate Reviews with Food Mentions
```python
from nlp.food_aware_generator import FoodAwareReviewGenerator

gen = FoodAwareReviewGenerator(
    'data/templates.json',
    'data/buckets.json',
    'data/food_items.json'
)

# Generate review mentioning specific foods
review = gen.generate_review(
    business_name="Rati Kaka Ni Bhajipav",
    level="medium",
    food_items=['pongal', 'dosa', 'samosa']
)

print(review)
# Output: "My visit to Rati Kaka Ni Bhajipav was wonderful. The pongal 
#          was absolutely delicious! Staff were very polite. 
#          Highly recommend trying the samosa."
```

---

## Food-Specific Templates

### Praise Templates
```
- "The {food} was absolutely delicious!"
- "I really enjoyed the {food}."
- "Their {food} is fantastic."
- "The {food} was cooked to perfection."
- "I was impressed by the {food}."
- "Their {food} is definitely worth trying."
- "The {food} melted in my mouth."
- "Best {food} I've had in a while."
```

### Recommend Templates
```
- "Highly recommend trying the {food}."
- "Don't miss their {food}."
- "The {food} is a must-try."
- "You have to try their {food}."
- "If you visit, order the {food}."
- "Their {food} is something special."
- "Make sure to get the {food}."
- "The {food} is their signature dish."
```

### Portion Templates
```
- "The {food} portions are generous."
- "Great portion size for the {food}."
- "Plenty of {food} on the plate."
- "The {food} serving was substantial."
```

---

## Database Structure

### `data/food_items.json`
```json
{
  "rati kaka ni bhajipav": [
    "pongal",
    "dosa",
    "idly",
    "samosa",
    "biryani"
  ],
  "trattoria roma": [
    "cacio e pepe",
    "carbonara",
    "pasta marinara",
    "risotto",
    "gnocchi"
  ],
  "golden dragon": [
    "fried rice",
    "chow mein",
    "sweet and sour chicken",
    "dim sum",
    "spring roll"
  ]
}
```

---

## Generation Examples

### Indian Restaurant
**Menu:** pongal, dosa, idly, samosa, biryani

**Generated Review:**
> "I recently visited Rati Kaka Ni Bhajipav and was very impressed. The biryani was absolutely delicious! Staff were very polite and attentive. Highly recommend trying the pongal."

### Italian Restaurant
**Menu:** cacio e pepe, carbonara, pasta marinara, risotto, lasagna

**Generated Review:**
> "My visit to Trattoria Roma was wonderful. Their cacio e pepe is fantastic. Excellent service with friendly staff. Don't miss their carbonara."

### Chinese Restaurant
**Menu:** fried rice, chow mein, sweet and sour chicken, dim sum, spring roll

**Generated Review:**
> "I had a great experience at Golden Dragon. The fried rice was cooked to perfection! Staff went above and beyond. Highly recommend trying the dim sum."

---

## Implementation Workflow

### For Menu Image Processing

1. **Capture menu image** from restaurant
2. **Run OCR** (Google Vision, Tesseract, etc.) to extract text
3. **Call extraction API:**
   ```bash
   POST /api/extract-foods
   {
     "menu_text": "<OCR output>",
     "cuisine_type": "indian"
   }
   ```
4. **Review detected foods** (edit if needed)
5. **Add to database:**
   ```bash
   POST /api/add-menu
   {
     "restaurant": "Restaurant Name",
     "food_items": ["detected", "foods"]
   }
   ```
6. **Generate reviews** mentioning these foods

### For Manual Menu Entry

1. **Restaurant owner enters menu items**
2. **API adds to database:**
   ```bash
   POST /api/add-menu
   {
     "restaurant": "My Restaurant",
     "food_items": ["dish1", "dish2", "dish3"]
   }
   ```
3. **System generates reviews** automatically

---

## Features

✅ **Automatic Food Detection**
- Supports 50+ common food items across cuisines
- Extensible to add more foods
- Fuzzy matching for OCR errors

✅ **Per-Restaurant Customization**
- Different reviews for different restaurants
- Reviews mention specific menu items
- Database of all restaurant menus

✅ **Smart Templates**
- 3 types of food-specific templates (praise, recommend, portion)
- Mix with general templates for variety
- 3 difficulty levels with food integration

✅ **OCR-Friendly**
- Handles OCR errors with fuzzy matching
- Configurable cuisine types
- Learns from manual corrections

✅ **Multiple Cuisine Support**
- Indian, Italian, Chinese, Mexican, Thai, Japanese, American
- Easy to add more cuisines
- Cuisine-specific food detection

---

## Next Steps

1. **Test the API**
   - Add menus for different restaurants
   - Generate reviews with food mentions
   - See how variety increases

2. **Integrate OCR**
   - Use Google Vision, AWS Textract, or Tesseract
   - Extract menu text from images
   - Add detected foods to database

3. **Scale Up**
   - Add more restaurants and menus
   - Build web form for menu uploads
   - Track popular food items

4. **Analytics**
   - Count which foods appear most in reviews
   - Track sentiment by food type
   - Generate food-specific recommendations

---

## Summary

You now have a complete **food-aware review generation system** that:

✨ Detects food names from menus
✨ Stores menu items per restaurant
✨ Generates reviews mentioning specific dishes
✨ Supports different restaurants with different foods
✨ Handles OCR preprocessing
✨ Provides flexible API endpoints
✨ Works with all cuisines

**Different restaurants = Different reviews with different foods!** 🍽️
