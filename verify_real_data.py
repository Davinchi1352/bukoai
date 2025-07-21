"""
Verify that dashboard is showing real data from database.
"""

from app import create_app, db
from app.models.user import User
from app.models.book_generation import BookGeneration, BookStatus

def check_real_data():
    """Check real data in database."""
    app = create_app()
    
    with app.app_context():
        print("=== Checking Real Database Data ===\n")
        
        # Get first user for testing
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return
            
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Check books for this user
        total_books = BookGeneration.query.filter_by(user_id=user.id).count()
        completed_books = BookGeneration.query.filter_by(
            user_id=user.id,
            status=BookStatus.COMPLETED
        ).count()
        processing_books = BookGeneration.query.filter_by(
            user_id=user.id,
            status=BookStatus.PROCESSING
        ).count()
        
        print(f"\n📚 Books Statistics:")
        print(f"  Total Books: {total_books}")
        print(f"  Completed: {completed_books}")
        print(f"  Processing: {processing_books}")
        
        # Get some book details
        recent_books = BookGeneration.query.filter_by(user_id=user.id).order_by(
            BookGeneration.created_at.desc()
        ).limit(3).all()
        
        if recent_books:
            print(f"\n📖 Recent Books:")
            for book in recent_books:
                print(f"  - {book.title}")
                print(f"    Status: {book.status.value}")
                print(f"    Words: {book.final_words or 'N/A'}")
                print(f"    Pages: {book.final_pages or 'N/A'}")
                print(f"    Genre: {book.genre or 'N/A'}")
                print(f"    Created: {book.created_at}")
                print("")
        else:
            print("\n❌ No books found for this user")
            
        # Check word/page totals
        completed_books_list = BookGeneration.query.filter_by(
            user_id=user.id,
            status=BookStatus.COMPLETED
        ).all()
        
        total_words = sum(book.final_words or 0 for book in completed_books_list)
        total_pages = sum(book.final_pages or 0 for book in completed_books_list)
        
        print(f"\n📊 Content Statistics:")
        print(f"  Total Words: {total_words:,}")
        print(f"  Total Pages: {total_pages}")
        print(f"  Average Words per Book: {total_words // len(completed_books_list) if completed_books_list else 0:,}")
        
        print("\n✅ This is the REAL data that should appear in your dashboard!")
        print("If the dashboard shows different numbers, the APIs are not working correctly.")

if __name__ == '__main__':
    check_real_data()