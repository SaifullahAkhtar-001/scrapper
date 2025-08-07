# Web Scraper Backend

A Flask-based web scraper system that can scrape multiple e-commerce sites, starting with eBay. The system uses DOM-based parsing with BeautifulSoup and stores data in Supabase.

## Features

- **Multi-site scraping**: Extensible architecture for scraping multiple e-commerce sites
- **eBay scraper**: DOM-based scraping of eBay search results
- **Database integration**: Stores scraped data in Supabase
- **Rate limiting**: Built-in delays and retry mechanisms to avoid detection
- **RESTful API**: Full CRUD operations for keyword management
- **Error handling**: Comprehensive error handling and logging

## Project Structure

```
backend/
├── main.py                 # Flask application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── run_scraper.py         # Standalone scraper runner
├── test_ebay_scraper.py   # Test script for eBay scraper
├── config/
│   ├── __init__.py
│   └── supabase_client.py # Supabase database client
├── routes/
│   ├── __init__.py
│   └── keyword_routes.py  # Keyword CRUD API endpoints
├── services/
│   ├── __init__.py
│   └── keyword_service.py # Keyword business logic
└── scrapers/
    ├── __init__.py        # Scraper manager and registration
    ├── base_scraper.py    # Abstract base scraper class
    └── ebay_scraper.py    # eBay-specific scraper implementation
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup

Make sure you have the following tables in your Supabase database:

#### Keywords Table
```sql
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Scraped Listings Table
```sql
CREATE TABLE scraped_listings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    price DECIMAL(10,2),
    url TEXT NOT NULL UNIQUE,
    images TEXT[], -- Array of image URLs
    description TEXT,
    site TEXT NOT NULL,
    keyword TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Usage

### 1. Start the Flask Application

```bash
python main.py
```

The server will start on `http://localhost:5000`

### 2. API Endpoints

#### Keyword Management

- `GET /api/keywords` - Get all active keywords
- `GET /api/keywords/<id>` - Get specific keyword
- `POST /api/keywords` - Add multiple keywords
- `PUT /api/keywords/<id>` - Update keyword
- `DELETE /api/keywords/<id>` - Soft delete keyword
- `DELETE /api/keywords/<id>/permanent` - Hard delete keyword
- `GET /api/keywords/stats` - Get keyword statistics
- `POST /api/keywords/test` - Add test keywords

#### Scraper Endpoints

- `GET /api/test-scrapers` - Test scraper system
- `GET /api/test-ebay-scraper` - Test eBay scraper with first 2 keywords
- `POST /api/run-scrapers` - Run all registered scrapers

### 3. Add Keywords

Using Postman or curl:

```bash
curl -X POST http://localhost:5000/api/keywords \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["vintage cigars", "Fonseca cigars", "Montecristo cigars"]
  }'
```

### 4. Test the eBay Scraper

```bash
# Test with first 2 keywords
curl http://localhost:5000/api/test-ebay-scraper

# Run all scrapers
curl -X POST http://localhost:5000/api/run-scrapers
```

### 5. Standalone Scraper

You can also run the scraper directly without the Flask app:

```bash
python run_scraper.py
```

### 6. Test Script

Test the eBay scraper functionality:

```bash
python test_ebay_scraper.py
```

## eBay Scraper Details

The eBay scraper uses DOM-based parsing with BeautifulSoup to extract:

- **Title**: Listing title
- **Price**: Converted to decimal format
- **URL**: Full listing URL
- **Images**: Array of image URLs
- **Description**: Listing description/snippet
- **Site**: Always "ebay"
- **Keyword**: The search keyword used

### Features

- **Multiple selectors**: Uses various CSS selectors to handle different eBay page layouts
- **Rate limiting**: Random delays between requests (2-5 seconds)
- **Retry mechanism**: Automatic retries with exponential backoff
- **Duplicate prevention**: Checks for existing URLs before saving
- **Error handling**: Comprehensive error handling and logging

### URL Structure

The scraper builds eBay search URLs in this format:
```
https://www.ebay.com/sch/i.html?_nkw={keyword}&_sacat=0&_pgn={page}
```

## Adding New Scrapers

To add a new scraper for another site:

1. Create a new file in `scrapers/` (e.g., `amazon_scraper.py`)
2. Inherit from `BaseScraper`
3. Implement the abstract methods:
   - `build_search_url(keyword, page)`
   - `extract_listings_from_page(html_content, keyword)`
4. Register the scraper in `scrapers/__init__.py`

Example:
```python
from .base_scraper import BaseScraper

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__("amazon")
    
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # Implement Amazon search URL building
        pass
    
    def extract_listings_from_page(self, html_content: str, keyword: str):
        # Implement Amazon listing extraction
        pass
```

## Craigslist Scraper - Selenium Requirements

To scrape Craigslist (searchcraigslist.net) results, you must use Selenium to render JavaScript-loaded content.

### Install Selenium

```
pip install selenium
```

### Install Google Chrome
- Download and install Google Chrome: https://www.google.com/chrome/

### Install ChromeDriver
- Download ChromeDriver matching your Chrome version: https://sites.google.com/chromium.org/driver/
- Add the ChromeDriver executable to your system PATH, or specify its path in the code:
  ```python
  driver = webdriver.Chrome(executable_path='path/to/chromedriver', options=chrome_options)
  ```

### Windows Troubleshooting
- If you get errors about ChromeDriver not found, ensure the folder containing chromedriver.exe is in your PATH.
- You can check your Chrome version by navigating to chrome://settings/help in your browser.

### Notes
- The scraper will not work in headless server environments without Chrome and ChromeDriver.
- If you want to use Firefox, install geckodriver and change the Selenium code accordingly.

## Error Handling

The system includes comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **Parsing errors**: Graceful handling of malformed HTML
- **Database errors**: Logging and continuation
- **Rate limiting**: Automatic delay increases

## Rate Limiting

The scraper implements several rate limiting measures:

- Random delays between requests (2-5 seconds)
- Longer delays between keywords (3-7 seconds)
- Exponential backoff on failures
- Dynamic user agent rotation

## Monitoring

The scraper provides detailed logging and monitoring:

- Progress updates for each keyword
- Success/failure counts
- Timing information
- Error details

## Troubleshooting

### Common Issues

1. **No keywords found**: Add keywords using the API endpoints
2. **Database connection failed**: Check your `.env` file and Supabase credentials
3. **No listings found**: This might be normal for some keywords or eBay might be blocking requests
4. **Import errors**: Make sure all dependencies are installed

### Debug Mode

Run the Flask app in debug mode for detailed error messages:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Security Considerations

- Never commit your `.env` file to version control
- Use environment variables for sensitive data
- Implement proper authentication for production use
- Consider using proxies for large-scale scraping
- Respect robots.txt and site terms of service

## License

This project is for educational purposes. Please respect the terms of service of the websites you scrape. 