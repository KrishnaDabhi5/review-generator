try:
    from nltk.tokenize import sent_tokenize as _nltk_sent_tokenize
    # verify punkt resource available once
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
    except Exception:
        _nltk_sent_tokenize = None
except Exception:
    _nltk_sent_tokenize = None


def sent_tokenize(text):
    """Safely tokenize sentences with fallback if NLTK unavailable."""
    if not text:
        return []
    
    # Try NLTK first
    if _nltk_sent_tokenize:
        try:
            return _nltk_sent_tokenize(text)
        except LookupError:
            pass
    
    # Fallback: simple regex split on sentence boundaries
    import re
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def extract_sentences(text):
    """Extract sentences from text."""
    if not text:
        return []
    return sent_tokenize(text)


def bucket_sentences(sentences):
    """Intelligent rule-based bucketing using contextual keywords.
    
    Categories:
    - opening: first impression, ambience, arrival experience
    - service: staff behavior, attentiveness, politeness
    - food: taste, quality, dishes
    - ambience: atmosphere, decor, music, environment
    - closing: recommendation, intent to return
    """
    buckets = {"opening": [], "service": [], "food": [], "ambience": [], "closing": []}
    
    # Define keyword sets
    opening_kw = [
        "great", "pleasant", "nice", "lovely", "wonderful", "excellent", 
        "amazing", "fantastic", "experience", "visited", "arrived", "walked in",
        "beautiful", "charming", "delightful"
    ]
    
    service_kw = [
        "service", "staff", "waiter", "waitress", "server", "attentive",
        "helpful", "polite", "courteous", "friendly", "quick", "prompt",
        "professional", "efficient", "team", "crew"
    ]
    
    food_kw = [
        "food", "taste", "delicious", "quality", "dish", "dishes", "meal",
        "cuisine", "flavor", "flavours", "flavorful", "fresh", "hot", "cold",
        "cooked", "prepared", "recipe", "ingredients", "pasta", "steak", "fish",
        "vegetarian", "appetizer", "dessert", "scrumptious"
    ]
    
    ambience_kw = [
        "ambience", "atmosphere", "decor", "decoration", "music", "cozy",
        "comfortable", "clean", "quiet", "noisy", "bright", "dim", "interior",
        "seating", "tables", "views", "layout", "environment", "spacious"
    ]
    
    closing_kw = [
        "recommend", "highly recommended", "visit again", "will go back",
        "must try", "come back", "worth", "worthwhile", "definitely", 
        "should visit", "try it", "go there", "favourite", "favorite",
        "best", "love", "adore"
    ]
    
    # Classify sentences
    for s in sentences:
        if not s or len(s) < 5:
            continue
        
        low = s.lower()
        
        # Check closing first (highest priority)
        if any(k in low for k in closing_kw):
            buckets["closing"].append(s)
        # Then service
        elif any(k in low for k in service_kw):
            buckets["service"].append(s)
        # Then food
        elif any(k in low for k in food_kw):
            buckets["food"].append(s)
        # Then ambience
        elif any(k in low for k in ambience_kw):
            buckets["ambience"].append(s)
        # Default to opening if it has positive sentiment
        elif any(k in low for k in opening_kw):
            buckets["opening"].append(s)
        # Fallback: food bucket for neutral sentences
        else:
            buckets["food"].append(s)
    
    return buckets
