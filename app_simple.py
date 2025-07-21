"""
Simplified Flask application for testing dashboard functionality.
No complex dependencies required.
"""

from flask import Flask, render_template, jsonify

def create_simple_app():
    """Create a simplified Flask app for testing."""
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config['SECRET_KEY'] = 'dev-secret-key-for-testing'
    
    # Mock current_user for templates
    @app.context_processor
    def inject_user():
        class MockUser:
            def __init__(self):
                self.is_authenticated = True
                self.first_name = "Usuario"
                self.id = 1
        
        return {'current_user': MockUser()}
    
    # Routes
    @app.route('/')
    def index():
        return '<h1>Buko AI - Simplified App</h1><p><a href="/dashboard">Go to Dashboard</a></p>'
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard del usuario."""
        return render_template('dashboard_compact.html')
    
    # Simplified API routes for dashboard
    from datetime import datetime, timedelta
    import random
    
    @app.route('/api/stats/dashboard', methods=['GET'])
    def get_dashboard_stats():
        """Get dashboard statistics - simplified version."""
        stats = {
            'total_books': random.randint(5, 25),
            'completed_books': random.randint(3, 20),
            'processing_books': random.randint(0, 3),
            'books_this_month': random.randint(1, 8),
            'total_books_change': random.randint(-2, 5),
            'completed_books_change': random.randint(0, 4),
            'monthly_books_change': random.randint(0, 3)
        }
        return jsonify(stats)
    
    @app.route('/api/stats/analytics', methods=['GET'])
    def get_analytics():
        """Get analytics data."""
        analytics = {
            'books_by_genre': [
                {'genre': 'Tecnología', 'count': 4, 'avg_words': 12500, 'avg_pages': 50},
                {'genre': 'Negocios', 'count': 3, 'avg_words': 9800, 'avg_pages': 39},
                {'genre': 'Educación', 'count': 2, 'avg_words': 8500, 'avg_pages': 34}
            ],
            'books_by_format': [
                {'format': 'pocket', 'count': 6, 'avg_pages': 35},
                {'format': 'standard', 'count': 3, 'avg_pages': 48}
            ],
            'download_formats': [
                {'format': 'PDF', 'count': 8, 'total_downloads': 12},
                {'format': 'EPUB', 'count': 6, 'total_downloads': 8},
                {'format': 'DOCX', 'count': 4, 'total_downloads': 4}
            ]
        }
        return jsonify(analytics)
    
    @app.route('/api/books', methods=['GET'])
    def get_books():
        """Get user's books - simplified version."""
        book_titles = [
            "Guía Completa de Python para Principiantes",
            "Marketing Digital en la Era de la IA",
            "Introducción a la Ciencia de Datos",
            "Desarrollo Web con Flask y React",
            "Finanzas Personales para Millennials"
        ]
        
        statuses = ['completed', 'processing', 'error']
        books = []
        
        for i, title in enumerate(book_titles):
            created_date = datetime.now() - timedelta(days=random.randint(1, 30))
            status = random.choice(statuses)
            # Bias towards completed
            if random.random() < 0.7:
                status = 'completed'
                
            book = {
                'id': i + 1,
                'title': title,
                'status': status,
                'created_at': created_date.isoformat(),
                'word_count': random.randint(1500, 8000)
            }
            books.append(book)
        
        return jsonify({'books': books, 'total': len(books)})
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'simple-app'})
    
    # Mock routes for navigation (needed for url_for in templates)
    @app.route('/books/generate')
    def generate_book():
        return '<h1>Generate Book</h1><p><a href="/dashboard">Back to Dashboard</a></p>'
    
    @app.route('/books/my-books')
    def my_books():
        return '<h1>My Books</h1><p><a href="/dashboard">Back to Dashboard</a></p>'
    
    @app.route('/auth/profile')
    def profile():
        return '<h1>Profile</h1><p><a href="/dashboard">Back to Dashboard</a></p>'
    
    @app.route('/help')
    def help():
        return '<h1>Help</h1><p><a href="/dashboard">Back to Dashboard</a></p>'
    
    # Additional routes needed for url_for in templates
    def mock_route():
        return '<h1>Mock Route</h1><p><a href="/dashboard">Back to Dashboard</a></p>'
    
    # Create all the routes that base.html template expects
    app.add_url_rule('/', 'main.index', index)
    app.add_url_rule('/dashboard', 'main.dashboard', dashboard)
    app.add_url_rule('/books/generate', 'books.generate', generate_book)
    app.add_url_rule('/books/my-books', 'books.my_books', my_books)
    app.add_url_rule('/auth/profile', 'auth.profile', profile)
    app.add_url_rule('/auth/login', 'auth.login', mock_route)
    app.add_url_rule('/auth/register', 'auth.register', mock_route)
    app.add_url_rule('/auth/logout', 'auth.logout', mock_route)
    app.add_url_rule('/help', 'main.help', help)
    app.add_url_rule('/features', 'main.features', mock_route)
    app.add_url_rule('/pricing', 'main.pricing', mock_route)
    app.add_url_rule('/subscription', 'main.subscription', mock_route)
    app.add_url_rule('/about', 'main.about', mock_route)
    app.add_url_rule('/contact', 'main.contact', mock_route)
    app.add_url_rule('/blog', 'main.blog', mock_route)
    app.add_url_rule('/faq', 'main.faq', mock_route)
    app.add_url_rule('/status', 'main.status', mock_route)
    app.add_url_rule('/privacy', 'main.privacy', mock_route)
    app.add_url_rule('/terms', 'main.terms', mock_route)
    app.add_url_rule('/cookies', 'main.cookies', mock_route)
    app.add_url_rule('/api-docs', 'main.api_docs', mock_route)
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("Starting simplified Flask app...")
    print("Dashboard available at: http://localhost:5002/dashboard")
    app.run(host='0.0.0.0', port=5002, debug=True)