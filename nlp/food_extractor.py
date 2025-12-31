"""
Food item extraction from menu images and text.
Supports OCR-based and manual food item lists.
"""
import json
import re
import os
from typing import List, Dict, Set
from pathlib import Path

class FoodItemExtractor:
    """
    Extract and manage food items from restaurant menus.
    """
    
    def __init__(self, food_db_path: str = "data/food_items.json"):
        """
        Initialize food item extractor.
        
        Args:
            food_db_path: Path to store food items database
        """
        self.food_db_path = food_db_path
        self.food_db = self._load_food_db()
        
        # Common food item patterns and variants
        self.common_foods = {
            'indian': ['dosa', 'pongal', 'idly', 'vada', 'samosa', 'biryani', 'dal', 
                      'curry', 'naan', 'roti', 'paratha', 'upma', 'uttapam', 'paneer',
                      'butter chicken', 'tandoori', 'kabab', 'tikka', 'masala', 'korma',
                      'ghobi manchurian', 'chow mein', 'fried rice'],
            'italian': ['pizza', 'pasta', 'risotto', 'ravioli', 'cannelloni', 'lasagna',
                       'cacio e pepe', 'carbonara', 'bolognese', 'marinara', 'alfredo',
                       'pesto', 'arrabbiata', 'gnocchi', 'polenta'],
            'chinese': ['fried rice', 'chow mein', 'chow fun', 'lo mein', 'sweet sour',
                       'kung pao', 'mapo tofu', 'dim sum', 'dumpling', 'spring roll'],
            'mexican': ['tacos', 'burrito', 'enchilada', 'quesadilla', 'nachos', 'fajita',
                       'guacamole', 'salsa', 'tamale', 'tostada', 'chiles rellenos'],
            'american': ['burger', 'steak', 'ribs', 'wings', 'sandwich', 'salad', 'fries',
                        'chicken', 'bacon', 'hotdog', 'meatloaf'],
            'thai': ['pad thai', 'green curry', 'red curry', 'tom yum', 'tom kha',
                    'satay', 'spring roll', 'pad see ew', 'basil chicken'],
            'japanese': ['sushi', 'ramen', 'tempura', 'tonkatsu', 'teriyaki', 'edamame',
                        'miso soup', 'gyoza', 'yakitori', 'donburi'],
        }
    
    def _load_food_db(self) -> Dict[str, List[str]]:
        """Load food database from JSON file."""
        try:
            if os.path.exists(self.food_db_path):
                with open(self.food_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load food database: {e}")
        return {}
    
    def _save_food_db(self):
        """Save food database to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.food_db_path) or '.', exist_ok=True)
            with open(self.food_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.food_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save food database: {e}")
    
    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract food items from text using pattern matching.
        
        Args:
            text: Menu text or description
            
        Returns:
            List of detected food items
        """
        text_lower = text.lower()
        detected_foods = []
        
        # Check against all known foods
        for cuisine_foods in self.common_foods.values():
            for food in cuisine_foods:
                if food.lower() in text_lower:
                    detected_foods.append(food)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_foods = []
        for food in detected_foods:
            if food.lower() not in seen:
                seen.add(food.lower())
                unique_foods.append(food)
        
        return unique_foods
    
    def add_restaurant_foods(self, restaurant_name: str, menu_items: List[dict]):
        """
        Add food items with ranks for a restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            menu_items: List of dicts with 'name' and 'rank' keys
        """
        # Clean and validate menu items
        cleaned_items = []
        seen = set()
        
        for item in menu_items:
            if not isinstance(item, dict):
                continue
                
            name = str(item.get('name', '')).strip().lower()
            rank = int(item.get('rank', 0)) or 0
            
            if name and name not in seen:
                cleaned_items.append({
                    'name': name,
                    'rank': rank
                })
                seen.add(name)
        
        # Sort by rank (ascending) before storing
        cleaned_items.sort(key=lambda x: (x['rank'], x['name']))
        
        # Store in database
        self.food_db[restaurant_name.lower()] = cleaned_items
        self._save_food_db()
        
        print(f"✅ Added {len(cleaned_items)} ranked food items for '{restaurant_name}'")
    
    def get_restaurant_foods(self, restaurant_name: str, include_ranks: bool = False) -> List[dict]:
        """
        Get food items for a specific restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            include_ranks: Whether to include rank information in the output
            
        Returns:
            List of food items (with ranks if include_ranks=True)
        """
        items = self.food_db.get(restaurant_name.lower(), [])
        
        if not include_ranks or not items or not isinstance(items[0], dict):
            # Backward compatibility: return just names if data is in old format
            return items if include_ranks else [item['name'] if isinstance(item, dict) else item for item in items]
            
        return sorted(items, key=lambda x: (x.get('rank', 0), x.get('name', '')))
    
    def extract_from_ocr_text(self, ocr_text: str, cuisine_type: str = None) -> List[str]:
        """
        Extract food items from OCR-processed menu text.
        More lenient matching for OCR errors.
        
        Args:
            ocr_text: Text from OCR processing
            cuisine_type: Type of cuisine (optional)
            
        Returns:
            List of detected food items
        """
        foods_to_check = []
        
        if cuisine_type:
            foods_to_check = self.common_foods.get(cuisine_type.lower(), [])
        
        if not foods_to_check:
            for cuisine_foods in self.common_foods.values():
                foods_to_check.extend(cuisine_foods)
        
        ocr_lower = ocr_text.lower()
        detected = []
        
        for food in foods_to_check:
            # Fuzzy matching for OCR errors
            if self._fuzzy_match(food, ocr_lower):
                detected.append(food)
        
        return list(dict.fromkeys(detected))  # Remove duplicates
    
    def _fuzzy_match(self, pattern: str, text: str, threshold: float = 0.8) -> bool:
        """
        Fuzzy string matching for OCR error tolerance.
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            threshold: Match similarity threshold (0-1)
            
        Returns:
            True if match found
        """
        # Simple substring match first
        if pattern.lower() in text:
            return True
        
        # Check for partial matches (at least 70% of pattern)
        pattern_words = pattern.split()
        for word in pattern_words:
            if len(word) > 2 and word in text:
                return True
        
        return False
    
    def get_all_restaurants(self) -> List[str]:
        """Get all restaurants in database."""
        return list(self.food_db.keys())
    
    def delete_restaurant(self, restaurant: str) -> bool:
        """
        Delete a restaurant and its menu from database.
        
        Args:
            restaurant: Restaurant name to delete
            
        Returns:
            True if deleted, False if not found
        """
        restaurant_lower = restaurant.lower()
        
        # Find the exact key (case-insensitive)
        for key in list(self.food_db.keys()):
            if key.lower() == restaurant_lower:
                del self.food_db[key]
                self._save_food_db()
                return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        total_restaurants = len(self.food_db)
        total_items = 0
        ranked_items = 0
        
        # Count items and check how many have ranks
        for items in self.food_db.values():
            if not items:
                continue
                
            total_items += len(items)
            
            # Check if items have rank information
            if isinstance(items[0], dict):
                ranked_items += sum(1 for item in items if item.get('rank', 0) > 0)
        
        return {
            'total_restaurants': total_restaurants,
            'total_menu_items': total_items,
            'ranked_menu_items': ranked_items,
            'average_items_per_restaurant': total_items / total_restaurants if total_restaurants > 0 else 0,
            'ranking_coverage': (ranked_items / total_items) if total_items > 0 else 0
        }


# Example usage and common food mappings
CUISINE_KEYWORDS = {
    'indian': ['dal', 'curry', 'naan', 'tandoori', 'biryani', 'masala'],
    'italian': ['pizza', 'pasta', 'risotto', 'carbonara', 'pesto'],
    'chinese': ['fried rice', 'chow mein', 'wonton', 'dim sum'],
    'mexican': ['taco', 'burrito', 'enchilada', 'salsa'],
    'thai': ['pad thai', 'curry', 'tom yum', 'satay'],
    'american': ['burger', 'steak', 'rib', 'wing', 'sandwich'],
}
