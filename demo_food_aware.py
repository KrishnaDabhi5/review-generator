"""
Demonstration of food-aware review generation.
Shows how specific menu items are incorporated into reviews.
"""
from nlp.food_extractor import FoodItemExtractor
from nlp.food_aware_generator import FoodAwareReviewGenerator

print("\n" + "="*75)
print("FOOD-AWARE REVIEW GENERATOR DEMONSTRATION")
print("="*75)

# Initialize systems
food_extractor = FoodItemExtractor('data/food_items.json')
generator = FoodAwareReviewGenerator('data/templates.json', 'data/buckets.json', 'data/food_items.json')

# Example 1: Indian Restaurant
print("\n[1] INDIAN RESTAURANT - Rati Kaka Ni Bhajipav")
print("-"*75)

indian_foods = ['pongal', 'idly', 'vada', 'samosa', 'biryani', 'dosa', 'uttapam', 'ghobi manchurian']
food_extractor.add_restaurant_foods("Rati Kaka Ni Bhajipav", indian_foods)

print(f"Menu items: {', '.join(indian_foods)}\n")

for i in range(2):
    review = generator.generate_review("Rati Kaka Ni Bhajipav", "medium", indian_foods)
    print(f"[Review {i+1}]")
    print(review)
    print()

# Example 2: Italian Restaurant
print("\n[2] ITALIAN RESTAURANT - Trattoria Roma")
print("-"*75)

italian_foods = ['cacio e pepe', 'carbonara', 'pasta marinara', 'risotto', 'gnocchi', 'pizza', 'lasagna']
food_extractor.add_restaurant_foods("Trattoria Roma", italian_foods)

print(f"Menu items: {', '.join(italian_foods)}\n")

for i in range(2):
    review = generator.generate_review("Trattoria Roma", "medium", italian_foods)
    print(f"[Review {i+1}]")
    print(review)
    print()

# Example 3: Chinese Restaurant
print("\n[3] CHINESE RESTAURANT - Golden Dragon")
print("-"*75)

chinese_foods = ['fried rice', 'chow mein', 'sweet and sour chicken', 'dim sum', 'spring roll', 'lo mein']
food_extractor.add_restaurant_foods("Golden Dragon", chinese_foods)

print(f"Menu items: {', '.join(chinese_foods)}\n")

for i in range(2):
    review = generator.generate_review("Golden Dragon", "medium", chinese_foods)
    print(f"[Review {i+1}]")
    print(review)
    print()

# Example 4: Detailed review with multiple food items
print("\n[4] DETAILED REVIEW - Mentioning Multiple Dishes")
print("-"*75)

print("Restaurant: Rati Kaka Ni Bhajipav")
print("Level: Detailed (mentions multiple food items)\n")

detailed_review = generator.generate_review("Rati Kaka Ni Bhajipav", "detailed", indian_foods)
print(detailed_review)

# Show database stats
print("\n" + "="*75)
print("DATABASE STATISTICS")
print("="*75)

stats = food_extractor.get_stats()
all_restaurants = food_extractor.get_all_restaurants()

print(f"\nTotal Restaurants: {stats['total_restaurants']}")
print(f"Total Food Items Tracked: {stats['total_unique_foods']}")
print(f"Average Items per Restaurant: {stats['average_items_per_restaurant']:.1f}")
print(f"\nRegistered Restaurants:")
for rest in all_restaurants:
    foods = food_extractor.get_restaurant_foods(rest)
    print(f"  • {rest.title()}: {len(foods)} items")

print("\n" + "="*75)
print("✅ Food-aware reviews generated successfully!")
print("   Each review mentions specific menu items from the restaurant")
print("="*75 + "\n")
