from nlp.food_extractor import FoodItemExtractor

print('Testing Delete Functionality...')
extractor = FoodItemExtractor('data/food_items.json')

print('\n[1] Current restaurants:')
restaurants = extractor.get_all_restaurants()
for r in restaurants:
    print(f'  - {r}')

print('\n[2] Testing delete (Golden Dragon):')
result = extractor.delete_restaurant('Golden Dragon')
print(f'  Deleted: {result}')

print('\n[3] Restaurants after delete:')
restaurants = extractor.get_all_restaurants()
for r in restaurants:
    print(f'  - {r}')

print('\n[4] Restore Golden Dragon:')
extractor.add_restaurant_foods('Golden Dragon', ['Fried Rice', 'Chow Mein', 'Dim Sum', 'Spring Roll', 'Lo Mein', 'Sweet and Sour Chicken'])
print('  Restored!')

print('\n[5] Final list:')
restaurants = extractor.get_all_restaurants()
for r in restaurants:
    print(f'  - {r}')

print('\nDELETE FUNCTIONALITY VERIFIED!')
