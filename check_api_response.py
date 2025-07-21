"""
Simple script to check API responses - what data is being returned.
"""

# Check what the simplified app returns
print("=== Checking Simplified App API Responses ===\n")

# Import the simplified app
from app_simple import create_simple_app

app = create_simple_app()

with app.test_client() as client:
    # Check dashboard stats
    print("1. Dashboard Stats API (/api/stats/dashboard):")
    response = client.get('/api/stats/dashboard')
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Total Books: {data.get('total_books')}")
        print(f"   Completed: {data.get('completed_books')}")
        print(f"   Total Words: {data.get('total_words')}")
        print(f"   Total Cost: ${data.get('total_cost')}")
        print(f"   ⚠️  These are MOCK values - not from real database!")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    print("\n2. Books API (/api/books):")
    response = client.get('/api/books?limit=3')
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Total Books: {data.get('total')}")
        books = data.get('books', [])
        for book in books:
            print(f"   - {book['title']} ({book['status']})")
        print(f"   ⚠️  These are MOCK books - not from real database!")
    else:
        print(f"   ❌ Error: {response.status_code}")

print("\n=== Summary ===")
print("The dashboard is currently showing MOCK data from app_simple.py")
print("To show REAL data, the main app needs to:")
print("1. Have all dependencies installed (flask_login, etc.)")
print("2. Connect to the PostgreSQL database")
print("3. Use the api_real.py routes instead of api_analytics.py")
print("\nThe api_real.py file has been created with safe queries that will")
print("show real data once the app is properly running.")