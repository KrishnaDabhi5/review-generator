"""
Enhanced template-based review generator that mentions specific food items.
Uses restaurant menus to generate more personalized, authentic reviews.
"""
import json
import random
from typing import Optional, List
from nlp.food_extractor import FoodItemExtractor

class FoodAwareReviewGenerator:
    """
    Generate reviews mentioning specific food items from restaurant menus.
    Combines templates + dataset sentences + specific food names.
    """
    
    def __init__(self, templates_path: str, buckets_path: str, food_db_path: str = "data/food_items.json"):
        """
        Initialize the food-aware generator.
        
        Args:
            templates_path: Path to templates.json
            buckets_path: Path to buckets.json
            food_db_path: Path to food items database
        """
        self.templates = self._load_templates(templates_path)
        self.buckets = self._load_buckets(buckets_path)
        self.food_extractor = FoodItemExtractor(food_db_path)
        
        # Food-specific sentence templates
        self.food_templates = {
            'praise': [
                "The {food} was absolutely delicious!",
                "I really enjoyed the {food}.",
                "Their {food} is fantastic.",
                "The {food} here is outstanding.",
                "I had their {food} and loved it.",
                "The {food} was cooked to perfection.",
                "I was impressed by the {food}.",
                "Their {food} is definitely worth trying.",
                "The {food} melted in my mouth.",
                "Best {food} I've had in a while."
            ],
            'recommend': [
                "Highly recommend trying the {food}.",
                "Don't miss their {food}.",
                "The {food} is a must-try.",
                "You have to try their {food}.",
                "If you visit, order the {food}.",
                "Their {food} is something special.",
                "Make sure to get the {food}.",
                "The {food} is their signature dish.",
            ],
            'portion': [
                "The {food} portions are generous.",
                "Great portion size for the {food}.",
                "Plenty of {food} on the plate.",
                "The {food} serving was substantial.",
            ]
        }
    
    def _load_templates(self, path: str) -> dict:
        """Load templates from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load templates: {e}")
            return {}
    
    def _load_buckets(self, path: str) -> dict:
        """Load sentence buckets from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load buckets: {e}")
            return {}
    
    def generate_review(self, 
                       business_name: str, 
                       level: str = "medium",
                       food_items: List[str] = None,
                       city: str = "",
                       seo_keywords: List[str] = None) -> str:
        """
        Generate a review mentioning specific food items.
        
        Args:
            business_name: Name of the restaurant
            level: Difficulty level (easy/medium/detailed)
            food_items: List of specific food items to mention (optional)
            city: City name for SEO-friendly context
            seo_keywords: List of SEO keywords to include in the review
            
        Returns:
            Generated review string
        """
        if seo_keywords is None:
            seo_keywords = []
        # Get food items from database if not provided
        if food_items is None:
            food_items = self.food_extractor.get_restaurant_foods(business_name)
        
        if level == "easy":
            sentences = self._generate_easy(business_name, food_items, city, seo_keywords)
        elif level == "detailed":
            sentences = self._generate_detailed(business_name, food_items, city, seo_keywords)
        else:  # medium
            sentences = self._generate_medium(business_name, food_items, city, seo_keywords)
        
        return " ".join(sentences)
    
    def _get_random_food(self, food_items: List[str]) -> Optional[str]:
        """Get a random food item from list."""
        return random.choice(food_items) if food_items else None
    
    def _generate_easy(self, business_name: str, food_items: List[str], city: str = "", seo_keywords: List[str] = None) -> list:
        """Generate 2-sentence easy review."""
        if seo_keywords is None:
            seo_keywords = []
        sentences = []
        
        # Opening template
        if self.templates.get('opening'):
            opening = random.choice(self.templates['opening'])
            sentences.append(opening.format(business_name=business_name))
        
        # Food-specific sentence
        food = self._get_random_food(food_items)
        if food:
            template = random.choice(self.food_templates['praise'])
            sentences.append(template.format(food=food))
        
        return sentences
    
    def _generate_medium(self, business_name: str, food_items: List[str], city: str = "", seo_keywords: List[str] = None) -> list:
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
        
        # 3. Food with specific item
        if food_items:
            food = self._get_random_food(food_items)
            if random.random() < 0.6:
                template = random.choice(self.food_templates['praise'])
                sentences.append(template.format(food=food))
            else:
                template = random.choice(self.food_templates['portion'])
                sentences.append(template.format(food=food))
        else:
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
        
        # 5. Closing with optional food recommendation
        if food_items and random.random() < 0.4:
            food = self._get_random_food(food_items)
            template = random.choice(self.food_templates['recommend'])
            sentences.append(template.format(food=food))
        else:
            if self.templates.get('closing'):
                sentences.append(random.choice(self.templates['closing']))
        
        # Trim to 4 sentences if we added city/SEO
        return sentences[:4]
    
    def _generate_detailed(self, business_name: str, food_items: List[str], city: str = "", seo_keywords: List[str] = None) -> list:
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
        
        # 3. Environment/atmosphere
        env_opts = []
        if self.templates.get('environment'):
            env_opts.extend(self.templates['environment'])
        if self.buckets.get('ambience'):
            env_opts.extend(self.buckets['ambience'])
        if env_opts:
            sentences.append(random.choice(env_opts))
        
        # 4. Food details with specific items
        if food_items:
            foods_to_mention = random.sample(food_items, min(2, len(food_items)))
            food_praise = []
            for food in foods_to_mention:
                template = random.choice(self.food_templates['praise'])
                food_praise.append(template.format(food=food))
            sentences.append(" ".join(food_praise))
        else:
            food_opts = []
            if self.templates.get('food'):
                food_opts.extend(self.templates['food'])
            if self.buckets.get('food'):
                food_opts.extend(self.buckets['food'])
            if food_opts:
                sentences.append(random.choice(food_opts))
        
        # 5. Service/staff details
        service_opts = []
        if self.templates.get('staff_specific'):
            service_opts.extend(self.templates['staff_specific'])
        if self.templates.get('speed'):
            service_opts.extend(self.templates['speed'])
        if self.buckets.get('service'):
            service_opts.extend(self.buckets['service'])
        if service_opts:
            sentences.append(random.choice(service_opts))
        
        # 6. Value/pricing
        if self.templates.get('value'):
            sentences.append(random.choice(self.templates['value']))
        
        # 7. Closing with food recommendation
        if food_items:
            food = self._get_random_food(food_items)
            template = random.choice(self.food_templates['recommend'])
            sentences.append(template.format(food=food))
        else:
            if self.templates.get('closing'):
                sentences.append(random.choice(self.templates['closing']))
        
        # Trim to 6 sentences if we added city/SEO
        return sentences[:6]
