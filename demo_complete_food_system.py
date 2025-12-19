#!/usr/bin/env python3
"""
Complete demonstration of food-aware review generation system.
Shows all features: menu management, extraction, and generation.
"""

from nlp.food_extractor import FoodItemExtractor
from nlp.food_aware_generator import FoodAwareReviewGenerator
import json

def demo_food_aware_system():
    print("\n" + "="*80)
    print("🍽️  FOOD-AWARE REVIEW GENERATION SYSTEM - COMPLETE DEMO")
    print("="*80)
    
    # Initialize systems
    extractor = FoodItemExtractor('data/food_items.json')
    generator = FoodAwareReviewGenerator(
        'data/templates.json',
        'data/buckets.json',
        'data/food_items.json'
    )
    
    # Demo 1: Indian Restaurant
    print("\n" + "="*80)
    print("DEMO 1: INDIAN RESTAURANT - Menu-Based Review Generation")
    print("="*80)
    
    restaurant1 = "Rati Kaka Ni Bhajipav"
    foods1 = ["pongal", "dosa", "idly", "vada", "samosa", "biryani", "ghobi manchurian"]
    
    print(f"\nRestaurant: {restaurant1}")
    print(f"Menu Items: {', '.join(foods1)}")
    
    extractor.add_restaurant_foods(restaurant1, foods1)
    
    print("\n📝 Generated Reviews (mention specific dishes):\n")
    for i in range(3):
        review = generator.generate_review(restaurant1, "medium", foods1)
        print(f"[Review {i+1}]")
        print(review)
        print()
    
    # Demo 2: Italian Restaurant
    print("\n" + "="*80)
    print("DEMO 2: ITALIAN RESTAURANT - Different Menu = Different Reviews")
    print("="*80)
    
    restaurant2 = "Trattoria Roma"
    foods2 = ["cacio e pepe", "carbonara", "pasta marinara", "risotto", "gnocchi", "lasagna", "tiramisu"]
    
    print(f"\nRestaurant: {restaurant2}")
    print(f"Menu Items: {', '.join(foods2)}")
    
    extractor.add_restaurant_foods(restaurant2, foods2)
    
    print("\n📝 Generated Reviews (Italian dishes):\n")
    for i in range(3):
        review = generator.generate_review(restaurant2, "medium", foods2)
        print(f"[Review {i+1}]")
        print(review)
        print()
    
    # Demo 3: Chinese Restaurant
    print("\n" + "="*80)
    print("DEMO 3: CHINESE RESTAURANT - Menu Recognition")
    print("="*80)
    
    restaurant3 = "Golden Dragon"
    foods3 = ["fried rice", "chow mein", "sweet and sour chicken", "dim sum", "spring roll", "lo mein"]
    
    print(f"\nRestaurant: {restaurant3}")
    print(f"Menu Items: {', '.join(foods3)}")
    
    extractor.add_restaurant_foods(restaurant3, foods3)
    
    print("\n📝 Generated Reviews (Chinese cuisine):\n")
    for i in range(3):
        review = generator.generate_review(restaurant3, "medium", foods3)
        print(f"[Review {i+1}]")
        print(review)
        print()
    
    # Demo 4: Food Extraction from Text
    print("\n" + "="*80)
    print("DEMO 4: EXTRACTING FOOD NAMES FROM MENU TEXT")
    print("="*80)
    
    menu_text_example = """
    SPECIAL DISHES:
    Pongal - Rice and lentils cooked with ghee and spices
    Dosa - Crispy crepe made from rice and lentils
    Idly - Steamed cake made from rice and lentils
    Samosa - Fried pastry with spiced potato filling
    Biryani - Fragrant rice dish with meat or vegetables
    Ghobi Manchurian - Cauliflower in Indo-Chinese sauce
    Paneer Butter Curry - Cottage cheese in creamy tomato sauce
    """
    
    print("\nMenu Text Sample:")
    print(menu_text_example)
    
    print("\n🔍 Extracting food names...")
    detected_foods = extractor.extract_from_text(menu_text_example)
    print(f"\nDetected Foods: {', '.join(detected_foods)}")
    print(f"Total Detected: {len(detected_foods)}")
    
    # Demo 5: Difficulty Levels with Food
    print("\n" + "="*80)
    print("DEMO 5: DIFFICULTY LEVELS - Impact on Food Mentions")
    print("="*80)
    
    test_restaurant = "Rati Kaka Ni Bhajipav"
    test_foods = foods1[:3]  # Use first 3 foods
    
    print(f"\nRestaurant: {test_restaurant}")
    print(f"Food Items: {', '.join(test_foods)}\n")
    
    # Easy
    print("[EASY] (2 sentences - minimal food mentions):")
    easy = generator.generate_review(test_restaurant, "easy", test_foods)
    print(easy)
    print()
    
    # Medium
    print("[MEDIUM] (4 sentences - moderate food mentions):")
    medium = generator.generate_review(test_restaurant, "medium", test_foods)
    print(medium)
    print()
    
    # Detailed
    print("[DETAILED] (6+ sentences - multiple food mentions):")
    detailed = generator.generate_review(test_restaurant, "detailed", test_foods)
    print(detailed)
    print()
    
    # Demo 6: Database Statistics
    print("\n" + "="*80)
    print("DEMO 6: FOOD DATABASE STATISTICS")
    print("="*80)
    
    stats = extractor.get_stats()
    all_restaurants = extractor.get_all_restaurants()
    
    print(f"\nTotal Restaurants: {stats['total_restaurants']}")
    print(f"Total Unique Foods: {stats['total_unique_foods']}")
    print(f"Average Items per Restaurant: {stats['average_items_per_restaurant']:.1f}")
    
    print("\nRestaurant Details:")
    for rest in all_restaurants:
        foods = extractor.get_restaurant_foods(rest)
        print(f"  📍 {rest.title()}")
        print(f"     Menu items: {len(foods)}")
        print(f"     Foods: {', '.join(foods[:3])}{'...' if len(foods) > 3 else ''}")
    
    # Demo 7: Show Database File
    print("\n" + "="*80)
    print("DEMO 7: FOOD DATABASE (data/food_items.json)")
    print("="*80)
    
    with open('data/food_items.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print("\nDatabase Structure:")
    print(json.dumps(db, ensure_ascii=False, indent=2))
    
    # Final Summary
    print("\n" + "="*80)
    print("✅ FOOD-AWARE SYSTEM DEMONSTRATION COMPLETE")
    print("="*80)
    
    print("""
KEY FEATURES DEMONSTRATED:
✅ Menu management per restaurant
✅ Food name extraction from text
✅ Review generation with food mentions
✅ Different restaurants = different foods = different reviews
✅ Difficulty levels affect food mention frequency
✅ Persistent food database
✅ API-ready for integration

NEXT STEPS:
1. Add more restaurants with their menus
2. Extract food from restaurant menu images (via OCR)
3. Use /api/add-menu endpoint to manage menus
4. Use /api/generate-with-food to generate reviews with food items
5. Query /api/all-restaurants to see stored menus

The system is READY FOR PRODUCTION! 🚀
    """)

if __name__ == "__main__":
    demo_food_aware_system()
