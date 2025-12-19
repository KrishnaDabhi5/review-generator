#!/usr/bin/env python3
"""Test menu input and API functionality."""
import requests
import json

def test_menu_api():
    print('Testing Menu Input API')
    print('=' * 50)
    print('')
    
    # Test 1: Add a new restaurant menu
    print('[1] Adding new restaurant: Spice Kitchen')
    payload = {
        'restaurant': 'Spice Kitchen',
        'food_items': ['Butter Chicken', 'Naan', 'Palak Paneer', 'Biryani', 'Samosa', 'Raita', 'Kheer']
    }
    try:
        r = requests.post('http://127.0.0.1:8001/api/add-menu', json=payload)
        if r.status_code == 200:
            result = r.json()
            print('   SUCCESS: ' + result['message'])
            print('   Items: ' + ', '.join(result['food_items']))
        else:
            print('   ERROR: ' + str(r.json().get('detail', 'Unknown error')))
    except Exception as e:
        print('   Connection error - is server running?')
        return
    
    print('')
    
    # Test 2: Add another restaurant
    print('[2] Adding new restaurant: Pasta Paradise')
    payload2 = {
        'restaurant': 'Pasta Paradise',
        'food_items': ['Carbonara', 'Lasagna', 'Penne Arrabbiata', 'Risotto', 'Tiramisu', 'Gelato']
    }
    try:
        r = requests.post('http://127.0.0.1:8001/api/add-menu', json=payload2)
        if r.status_code == 200:
            result = r.json()
            print('   SUCCESS: ' + result['message'])
            print('   Items: ' + ', '.join(result['food_items']))
    except Exception as e:
        print('   ERROR: ' + str(e))
    
    print('')
    
    # Test 3: View all restaurants
    print('[3] Viewing all registered restaurants')
    try:
        r = requests.get('http://127.0.0.1:8001/api/all-restaurants')
        if r.status_code == 200:
            result = r.json()
            print('   Total restaurants: ' + str(result['total_restaurants']))
            for restaurant in result['restaurants']:
                print('   - ' + restaurant)
    except Exception as e:
        print('   ERROR: ' + str(e))
    
    print('')
    
    # Test 4: Get specific restaurant foods
    print('[4] Getting Spice Kitchen menu')
    try:
        r = requests.get('http://127.0.0.1:8001/api/restaurant-foods/Spice Kitchen')
        if r.status_code == 200:
            result = r.json()
            print('   Restaurant: ' + result['restaurant'])
            print('   Foods: ' + ', '.join(result['food_items']))
            print('   Total: ' + str(result['total']))
    except Exception as e:
        print('   ERROR: ' + str(e))
    
    print('')
    print('=' * 50)
    print('Test complete! Visit http://127.0.0.1:8001/menu to use the web form')

if __name__ == '__main__':
    test_menu_api()
