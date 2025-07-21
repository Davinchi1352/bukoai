"""
Test script to verify real APIs are working.
"""

import requests
import json

# You need to be logged in for these to work
# Update the session cookie after logging in
COOKIES = {
    'session': 'YOUR_SESSION_COOKIE_HERE'  # Update this
}

BASE_URL = 'http://localhost:5001'

def test_dashboard_stats():
    """Test dashboard statistics API."""
    print("=== Testing Dashboard Stats API ===")
    response = requests.get(f'{BASE_URL}/api/stats/dashboard', cookies=COOKIES)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"Total Books: {data.get('total_books', 0)}")
        print(f"Completed: {data.get('completed_books', 0)}")
        print(f"Processing: {data.get('processing_books', 0)}")
        print(f"Total Words: {data.get('total_words', 0):,}")
        print(f"Total Cost: ${data.get('total_cost', 0):.2f}")
        print(f"Success Rate: {data.get('success_rate', 0)}%")
        
        if 'error' in data:
            print(f"⚠️  Error in response: {data['error']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_analytics():
    """Test analytics API."""
    print("\n=== Testing Analytics API ===")
    response = requests.get(f'{BASE_URL}/api/stats/analytics', cookies=COOKIES)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"Genres: {len(data.get('books_by_genre', []))} categories")
        print(f"Formats: {len(data.get('books_by_format', []))} formats")
        print(f"Download formats: {len(data.get('download_formats', []))} types")
        
        # Show first few items
        if data.get('books_by_genre'):
            print("\nTop Genres:")
            for genre in data['books_by_genre'][:3]:
                print(f"  - {genre['genre']}: {genre['count']} books")
                
        if 'error' in data:
            print(f"⚠️  Error in response: {data['error']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_books():
    """Test books API."""
    print("\n=== Testing Books API ===")
    response = requests.get(f'{BASE_URL}/api/books?limit=5', cookies=COOKIES)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"Total Books: {data.get('total', 0)}")
        print(f"Returned: {len(data.get('books', []))} books")
        
        # Show books
        if data.get('books'):
            print("\nRecent Books:")
            for book in data['books']:
                print(f"  - {book['title']} ({book['status']})")
                
        if 'error' in data:
            print(f"⚠️  Error in response: {data['error']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    print("Real API Testing Script")
    print("====================")
    print("Note: You need to update COOKIES['session'] with your actual session cookie")
    print("1. Login to the app at http://localhost:5001/auth/login")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Application/Storage -> Cookies")
    print("4. Copy the 'session' cookie value")
    print("5. Update COOKIES['session'] in this script")
    print("")
    
    # Uncomment after updating cookie
    # test_dashboard_stats()
    # test_analytics()
    # test_books()
    
    print("\nTo test without login, create a test user and use app context:")
    print("python3 -c \"from app import create_app; app=create_app(); print('App created')\"")