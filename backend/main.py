from flask import Flask, jsonify
from flask_cors import CORS
from config.supabase_client import supabase_client
from scrapers import scraper_manager
from routes.keyword_routes import keyword_bp

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend integration
CORS(app)

# Register blueprints
app.register_blueprint(keyword_bp)

# Basic route for testing
@app.route('/')
def home():
    return jsonify({
        'message': 'Flask app is running successfully!',
        'status': 'active'
    })

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'scrapper-backend'
    })

# Database connection test endpoint
@app.route('/api/test-db')
def test_database():
    try:
        # Test the connection by fetching keywords
        keywords = supabase_client.get_all_keywords()
        return jsonify({
            'success': True,
            'message': 'Database connection successful',
            'keywords_count': len(keywords),
            'sample_keywords': [kw['keyword'] for kw in keywords[:3]] if keywords else []
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

# Test scraper system endpoint
@app.route('/api/test-scrapers')
def test_scrapers():
    try:
        # Get keywords
        keywords = scraper_manager.get_keywords()
        
        # Check registered scrapers
        registered_scrapers = [scraper.site_name for scraper in scraper_manager.scrapers]
        
        return jsonify({
            'success': True,
            'keywords_count': len(keywords),
            'keywords': keywords,
            'registered_scrapers': registered_scrapers,
            'scrapers_count': len(registered_scrapers),
            'message': 'Scraper system is ready' if registered_scrapers else 'No scrapers registered'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Test eBay scraper endpoint
@app.route('/api/test-ebay-scraper')
def test_ebay_scraper():
    try:
        # Get keywords
        keywords = scraper_manager.get_keywords()
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': 'No keywords found in database. Please add some keywords first.'
            }), 400
        
        # Run eBay scraper with first 2 keywords for testing
        test_keywords = keywords[:2]
        
        print(f"Testing eBay scraper with keywords: {test_keywords}")
        
        # Get the eBay scraper
        ebay_scraper = None
        for scraper in scraper_manager.scrapers:
            if scraper.site_name == 'ebay':
                ebay_scraper = scraper
                break
        
        if not ebay_scraper:
            return jsonify({
                'success': False,
                'error': 'eBay scraper not found'
            }), 500
        
        # Run the scraper
        result = ebay_scraper.run(test_keywords)
        
        return jsonify({
            'success': True,
            'message': 'eBay scraper test completed',
            'test_keywords': test_keywords,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Run all scrapers endpoint
@app.route('/api/run-scrapers', methods=['POST'])
def run_all_scrapers():
    try:
        # Run all registered scrapers
        result = scraper_manager.run_all_scrapers()
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'All scrapers completed',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
