from flask import Flask, jsonify
from flask_cors import CORS
from routes.keyword_routes import keyword_bp
from services.health_service import HealthService
from services.database_service import DatabaseService
from services.scraper_service import ScraperService
from services.todocoleccion_service import TodocoleccionService

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend integration
CORS(app)

# Register blueprints
app.register_blueprint(keyword_bp)

# Basic route for testing
@app.route('/')
def home():
    return jsonify(HealthService.get_home_status())

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify(HealthService.get_health_status())

# Database connection test endpoint
@app.route('/api/test-db')
def test_database():
    result = DatabaseService.test_connection()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

# Test scraper system endpoint
@app.route('/api/test-scrapers')
def test_scrapers():
    result = ScraperService.get_scraper_status()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

# Test eBay scraper endpoint
@app.route('/api/test-ebay-scraper')
def test_ebay_scraper():
    result = ScraperService.test_ebay_scraper()
    status_code = 500 if not result.get('success', True) else 200
    if not result.get('success') and 'No keywords found' in result.get('error', ''):
        status_code = 400
    return jsonify(result), status_code

# Run all scrapers endpoint
@app.route('/api/run-scrapers', methods=['POST'])
def run_all_scrapers():
    result = ScraperService.run_all_scrapers()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

# Todocoleccion scraper routes
@app.route('/api/test-todocoleccion-scraper')
def test_todocoleccion_scraper():
    result = TodocoleccionService.test_todocoleccion_scraper()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

@app.route('/api/run-todocoleccion-scraper', methods=['POST'])
def run_todocoleccion_scraper():
    result = TodocoleccionService.run_todocoleccion_scraper()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

@app.route('/api/todocoleccion-status')
def todocoleccion_status():
    result = TodocoleccionService.get_todocoleccion_status()
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

@app.route('/api/scrape-todocoleccion/<keyword>')
def scrape_todocoleccion_keyword(keyword):
    result = TodocoleccionService.scrape_specific_keyword(keyword)
    status_code = 500 if not result.get('success', True) else 200
    return jsonify(result), status_code

@app.route('/api/push-cigar-listings', methods=['POST'])
def push_cigar_listings():
    result = TodocoleccionService.push_cigar_listings_from_scraped()
    status_code = 200 if result.get('success', False) else 500
    return jsonify(result), status_code

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
