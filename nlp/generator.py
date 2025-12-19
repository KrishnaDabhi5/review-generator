import random
import re


LEVEL_SENTENCE_COUNT = {"easy": 2, "medium": 4, "detailed": 6}

# Simple synonym patterns (word -> [alternatives])
SYNONYMS = {
    "great": ["wonderful", "excellent", "fantastic", "amazing", "outstanding"],
    "good": ["nice", "pleasant", "fine", "excellent", "wonderful"],
    "delicious": ["tasty", "scrumptious", "flavorful", "mouthwatering"],
    "food": ["cuisine", "dishes", "meal", "fare"],
    "staff": ["team", "service crew", "waiters"],
    "service": ["experience", "treatment"],
    "place": ["restaurant", "spot", "venue"],
    "nice": ["pleasant", "charming", "lovely", "delightful"],
    "quick": ["fast", "swift", "prompt"],
    "polite": ["courteous", "friendly", "warm"],
    "highly": ["very", "quite", "truly"],
    "must": ["definitely", "should"],
}


def _apply_simple_synonyms(sentence: str) -> str:
    """Apply simple word-level synonym replacements."""
    words = sentence.split()
    out = []
    for word in words:
        # Check for matches (case-insensitive)
        lower = word.lower()
        if lower in SYNONYMS and random.random() < 0.2:  # 20% replacement chance
            replacement = random.choice(SYNONYMS[lower])
            # Preserve capitalization if word was capitalized
            if word[0].isupper():
                replacement = replacement.capitalize()
            out.append(replacement)
        else:
            out.append(word)
    return " ".join(out)


def _reorder_sentences(sentences: list, level: str) -> list:
    """Reorder sentences for natural flow: opening → details → closing."""
    if not sentences:
        return []
    
    # Classify sentences
    opening = []
    details = []
    closing = []
    
    opening_keywords = ["great", "pleasant", "wonderful", "nice", "lovely", "excellent"]
    closing_keywords = ["recommend", "visit again", "will go back", "must try", "highly recommended"]
    
    for s in sentences:
        lower = s.lower()
        if any(k in lower for k in closing_keywords):
            closing.append(s)
        elif any(k in lower for k in opening_keywords):
            opening.append(s)
        else:
            details.append(s)
    
    # Build in natural order: opening(1) → details(middle) → closing(1)
    result = []
    if opening:
        result.append(random.choice(opening))
    if details:
        random.shuffle(details)
        result.extend(details)
    if closing:
        result.append(random.choice(closing))
    
    return result


def generate_review(buckets: dict, level: str = "medium", business_name: str = None) -> str:
    """Build a review by sampling from buckets.
    
    buckets: dict with lists for keys ['opening','service','food','ambience','closing']
    level: 'easy' (2 sent), 'medium' (4 sent), or 'detailed' (6 sent)
    business_name: optional business name to replace in the review
    
    Strategy:
    1. Sample sentences, preferring bucket diversity
    2. Reorder for natural flow (opening → details → closing)
    3. Apply simple synonym swaps for uniqueness
    4. Replace extracted names with business name
    5. Join with natural punctuation
    """
    level = level.lower()
    n_sentences = LEVEL_SENTENCE_COUNT.get(level, 4)
    
    # Get available buckets
    available = {k: v for k, v in buckets.items() if v}
    if not available:
        return ""
    
    bucket_order = ["opening", "service", "food", "ambience", "closing"]
    active_buckets = [b for b in bucket_order if b in available and available[b]]
    
    if not active_buckets:
        return ""
    
    # Select sentences: rotate through buckets to maximize diversity
    selected = []
    bucket_idx = 0
    while len(selected) < n_sentences and active_buckets:
        bucket = active_buckets[bucket_idx % len(active_buckets)]
        sent = random.choice(available[bucket])
        selected.append(sent)
        bucket_idx += 1
    
    # Reorder for natural flow
    ordered = _reorder_sentences(selected, level)
    
    # Apply synonym swaps
    final = [_apply_simple_synonyms(s) for s in ordered]
    
    # Join sentences naturally
    review = " ".join(final)
    
    # Ensure proper ending punctuation
    review = review.rstrip()
    if not review.endswith(('.', '!', '?')):
        review += "."
    
    # Replace extracted names with business name (if provided)
    if business_name:
        review = _replace_names_with_business(review, business_name)
    
    return review


def _replace_names_with_business(text: str, business_name: str) -> str:
    """Replace common first names and staff references with business name.
    
    Captures names like: abbie, john, maria, etc. and replaces with business name.
    """
    import re
    
    # List of common names to replace (case-insensitive)
    common_names = [
        'abbie', 'john', 'maria', 'james', 'sarah', 'michael', 'jessica',
        'david', 'emma', 'robert', 'anna', 'william', 'sophie', 'andre',
        'pierre', 'jean', 'marie', 'carlo', 'anna', 'marco', 'giulia'
    ]
    
    # Also replace standalone staff/waiter/bartender references when followed by a name
    for name in common_names:
        # Match: "name was", "name made", "name served", etc.
        pattern = rf'\b{name}\s+(was|made|served|told|gave|said|explained|showed)\b'
        replacement = rf'{business_name} \1'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Also match at sentence start
        pattern = rf'^{name}\s+'
        replacement = f'{business_name} '
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text
