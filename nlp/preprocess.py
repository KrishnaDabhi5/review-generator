import re
import pandas as pd
try:
    from nltk.tokenize import word_tokenize as _nltk_word_tokenize
    # check punkt resource once to avoid repeated LookupError during large maps
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
    except Exception:
        _nltk_word_tokenize = None
except Exception:
    _nltk_word_tokenize = None


def word_tokenize(text):
    if not isinstance(text, str):
        return []
    if _nltk_word_tokenize:
        try:
            return _nltk_word_tokenize(text)
        except Exception:
            return text.split()
    return text.split()


def load_dataset(path):
    return pd.read_csv(path)


def _remove_emojis(text):
    # basic removal of non-printable / emoji characters
    return re.sub(r"[^\x00-\x7F]+", "", text)


def _normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = _remove_emojis(text)
    text = text.replace("@", "")
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^\w\s\.\'\-]", "", text)
    text = text.lower()
    text = _normalize_whitespace(text)
    return text


def preprocess_dataframe(df: pd.DataFrame, review_col: str = "Review", rating_col: str = "Rating", sentiment_col: str = "Sentiment", min_rating: int = 4) -> pd.DataFrame:
    """Preprocess review dataframe.
    
    Args:
        df: Input dataframe
        review_col: Name of review text column
        rating_col: Name of rating column (optional, if exists)
        sentiment_col: Name of sentiment column (optional, if exists)
        min_rating: Minimum rating to keep (for numeric ratings)
    """
    df = df.copy()
    
    # Filter by sentiment (if Sentiment column exists)
    if sentiment_col in df.columns:
        df = df[df[sentiment_col].str.lower() == "positive"]
    
    # Filter by rating (if Rating column exists and no Sentiment filter was applied)
    elif rating_col in df.columns:
        df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
        df = df[df[rating_col] >= min_rating]
    
    # Clean review text
    if review_col in df.columns:
        df[review_col] = df[review_col].fillna("").astype(str).map(clean_text)
        # drop very short reviews (<5 words)
        df["_word_count"] = df[review_col].map(lambda t: len(word_tokenize(t)))
        df = df[df["_word_count"] >= 5].drop(columns=["_word_count"])
    
    return df
