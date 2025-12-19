import json
import random
from typing import Optional

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
    
    def generate_review(self, business_name: str, level: str = "medium") -> str:
        """
        Generate a review using templates and dataset sentences.
        
        Args:
            business_name: Name of the business to feature in the review
            level: Difficulty level - "easy" (2 sentences), "medium" (4 sentences), "detailed" (6+ sentences)
        
        Returns:
            Generated review string
        """
        if level == "easy":
            sentences = self._generate_easy(business_name)
        elif level == "detailed":
            sentences = self._generate_detailed(business_name)
        else:  # medium
            sentences = self._generate_medium(business_name)
        
        return " ".join(sentences)
    
    def _generate_easy(self, business_name: str) -> list:
        """Generate 2-sentence easy review."""
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
    
    def _generate_medium(self, business_name: str) -> list:
        """Generate 4-sentence medium review."""
        sentences = []
        
        # 1. Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # 2. Food template or dataset
        if random.random() < 0.6 and self.templates.get('food'):
            sentences.append(random.choice(self.templates['food']))
        elif self.buckets.get('food'):
            sentences.append(random.choice(self.buckets['food']))
        
        # 3. Service/staff template or dataset
        service_opts = []
        if self.templates.get('staff_specific'):
            service_opts.extend(self.templates['staff_specific'])
        if self.templates.get('service'):
            service_opts.extend(self.templates['service'])
        if self.buckets.get('service'):
            service_opts.extend(self.buckets['service'])
        
        if service_opts:
            sentences.append(random.choice(service_opts))
        
        # 4. Closing template
        if self.templates.get('closing'):
            closing = random.choice(self.templates['closing'])
            sentences.append(closing)
        
        return sentences
    
    def _generate_detailed(self, business_name: str) -> list:
        """Generate 6-sentence detailed review."""
        sentences = []
        
        # 1. Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # 2. Environment/atmosphere
        env_opts = []
        if self.templates.get('environment'):
            env_opts.extend(self.templates['environment'])
        if self.buckets.get('ambience'):
            env_opts.extend(self.buckets['ambience'])
        if env_opts:
            sentences.append(random.choice(env_opts))
        
        # 3. Food details
        food_opts = []
        if self.templates.get('food'):
            food_opts.extend(self.templates['food'])
        if self.buckets.get('food'):
            food_opts.extend(self.buckets['food'])
        if food_opts:
            sentences.append(random.choice(food_opts))
        
        # 4. Service/staff details
        service_opts = []
        if self.templates.get('staff_specific'):
            service_opts.extend(self.templates['staff_specific'])
        if self.templates.get('speed'):
            service_opts.extend(self.templates['speed'])
        if self.buckets.get('service'):
            service_opts.extend(self.buckets['service'])
        if service_opts:
            sentences.append(random.choice(service_opts))
        
        # 5. Value/pricing
        if self.templates.get('value'):
            sentences.append(random.choice(self.templates['value']))
        
        # 6. Closing template
        if self.templates.get('closing'):
            closing = random.choice(self.templates['closing'])
            sentences.append(closing)
        
        return sentences
