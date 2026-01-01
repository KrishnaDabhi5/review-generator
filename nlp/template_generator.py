import json
import random
from typing import Optional, List

class TemplateReviewGenerator:
    """
    Generate reviews using templates combined with dataset sentences.
    This approach provides more variety and reduces repetition.
    """
    
    def __init__(self, templates_path: str, buckets_path: str):
        """
        Initialize with template and bucket data.
        
        Args:
            templates_path: Path to templates.json
            buckets_path: Path to buckets.json (sentence buckets from dataset)
        """
        self.templates = self._load_templates(templates_path)
        self.buckets = self._load_buckets(buckets_path)
    
    def _load_templates(self, path: str) -> dict:
        """Load templates from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load templates from {path}: {e}")
            return {}
    
    def _load_buckets(self, path: str) -> dict:
        """Load sentence buckets from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load buckets from {path}: {e}")
            return {}
    
    def generate_review(self, business_name: str, level: str = "medium", city: str = "", seo_keywords: List[str] = None) -> str:
        """
        Generate a review using templates and dataset sentences.
        
        Args:
            business_name: Name of the business to feature in the review
            level: Difficulty level - "easy" (2 sentences), "medium" (4 sentences), "detailed" (6+ sentences)
            city: City name for SEO-friendly context
            seo_keywords: List of SEO keywords to include in the review
        
        Returns:
            Generated review string
        """
        if seo_keywords is None:
            seo_keywords = []
        if level == "easy":
            sentences = self._generate_easy(business_name, city, seo_keywords)
        elif level == "detailed":
            sentences = self._generate_detailed(business_name, city, seo_keywords)
        else:  # medium
            sentences = self._generate_medium(business_name, city, seo_keywords)
        
        return " ".join(sentences)
    
    def _generate_easy(self, business_name: str, city: str = "", seo_keywords: List[str] = None) -> list:
        """Generate 2-sentence easy review."""
        if seo_keywords is None:
            seo_keywords = []
        sentences = []
        
        # Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # Food or service from dataset
        if self.buckets.get('food') or self.buckets.get('service'):
            category = random.choice(['food', 'service'])
            if self.buckets.get(category):
                sentence = random.choice(self.buckets[category])
                sentences.append(sentence)
        
        return sentences
    
    def _generate_medium(self, business_name: str, city: str = "", seo_keywords: List[str] = None) -> list:
        """Generate 4-sentence medium review."""
        if seo_keywords is None:
            seo_keywords = []
        sentences = []
        
        # 1. Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # 2. Inject city or SEO keyword if available
        choices = ["none"]
        weights = [0.25]
        if city:
            choices.append("city")
            weights.append(0.45)
        if seo_keywords:
            choices.append("kw")
            weights.append(0.30)

        pick = random.choices(choices, weights=weights, k=1)[0]
        if pick == "city":
            city_lines = [
                f"In {city}, this spot is definitely worth a visit.",
                f"If you're around {city}, put this place on your list.",
                f"This is one of those places in {city} that you end up recommending.",
                f"Right in {city}, this place stood out for all the right reasons.",
                f"{city} has a lot of options, but this one really impressed me.",
            ]
            sentences.append(random.choice(city_lines))
        elif pick == "kw":
            kw = random.choice(seo_keywords)
            kw_lines = [
                f"A great choice if you're looking for {kw}.",
                f"Perfect for anyone craving {kw}.",
                f"If {kw} is what you want, you'll be happy here.",
                f"This place delivers when it comes to {kw}.",
                f"Easily one of the better spots for {kw} in the area.",
            ]
            sentences.append(random.choice(kw_lines))
        
        # 3. Food template or dataset
        if random.random() < 0.6 and self.templates.get('food'):
            sentences.append(random.choice(self.templates['food']))
        elif self.buckets.get('food'):
            sentences.append(random.choice(self.buckets['food']))
        
        # 4. Service/staff template or dataset
        service_opts = []
        if self.templates.get('staff_specific'):
            service_opts.extend(self.templates['staff_specific'])
        if self.templates.get('service'):
            service_opts.extend(self.templates['service'])
        if self.buckets.get('service'):
            service_opts.extend(self.buckets['service'])
        
        if service_opts:
            sentences.append(random.choice(service_opts))
        
        # 5. Closing template
        if self.templates.get('closing'):
            closing = random.choice(self.templates['closing'])
            sentences.append(closing)
        
        # Trim to 4 sentences if we added city/SEO
        return sentences[:4]
    
    def _generate_detailed(self, business_name: str, city: str = "", seo_keywords: List[str] = None) -> list:
        """Generate 6-sentence detailed review."""
        if seo_keywords is None:
            seo_keywords = []
        sentences = []
        
        # 1. Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # 2. Inject city or SEO keyword if available
        choices = ["none"]
        weights = [0.15]
        if city:
            choices.append("city")
            weights.append(0.55)
        if seo_keywords:
            choices.append("kw")
            weights.append(0.30)

        pick = random.choices(choices, weights=weights, k=1)[0]
        if pick == "city":
            city_lines = [
                f"In {city}, this place genuinely stands out.",
                f"If you're exploring {city}, this is a great stop.",
                f"One of my better finds in {city} recently.",
                f"This is the kind of place in {city} you come back to.",
                f"{city} has plenty of choices, but this one was a pleasant surprise.",
            ]
            sentences.append(random.choice(city_lines))
        elif pick == "kw":
            kw = random.choice(seo_keywords)
            kw_lines = [
                f"For anyone searching for {kw}, this place is a solid pick.",
                f"It really hits the mark if you're into {kw}.",
                f"This is a great option when {kw} is on your mind.",
                f"The overall {kw} experience here felt really well done.",
                f"If {kw} matters to you, you'll appreciate what they offer.",
            ]
            sentences.append(random.choice(kw_lines))
        
        # 3. Food template or dataset
        if random.random() < 0.6 and self.templates.get('food'):
            sentences.append(random.choice(self.templates['food']))
        elif self.buckets.get('food'):
            sentences.append(random.choice(self.buckets['food']))
        
        # 4. Service/staff template or dataset
        service_opts = []
        if self.templates.get('staff_specific'):
            service_opts.extend(self.templates['staff_specific'])
        if self.templates.get('service'):
            service_opts.extend(self.templates['service'])
        if self.buckets.get('service'):
            service_opts.extend(self.buckets['service'])
        
        if service_opts:
            sentences.append(random.choice(service_opts))
        
        # 5. Atmosphere/ambiance template or dataset
        if self.templates.get('ambiance'):
            sentences.append(random.choice(self.templates['ambiance']))
        elif self.buckets.get('ambiance'):
            sentences.append(random.choice(self.buckets['ambiance']))
        
        # 6. Closing template
        if self.templates.get('closing'):
            closing = random.choice(self.templates['closing'])
            sentences.append(closing)
        
        # Trim to 6 sentences if we added city/SEO
        return sentences[:6]
