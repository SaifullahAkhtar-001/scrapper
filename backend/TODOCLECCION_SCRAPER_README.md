# Todocoleccion Scraper

This document describes the Todocoleccion.net scraper implementation and how to use it.

## Overview

The Todocoleccion scraper is designed to extract listings from `https://www.todocoleccion.net/buscador` with the following features:

- **Pagination Support**: Handles multiple pages using the `P` parameter
- **Search Terms**: Uses the `bu` parameter for search keywords
- **Sort Order**: Uses `O=rl` for consistent sorting
- **404 Detection**: Stops scraping when a 404 error is encountered
- **Data Extraction**: Extracts image links, titles, descriptions, and prices

## URL Structure

The scraper builds URLs in the following format:
```
https://www.todocoleccion.net/buscador?P={page_number}&bu={search_term}&O=rl
```

Where:
- `P`: Page number (starts from 1)
- `bu`: Search term (URL encoded)
- `O=rl`: Sort order (relevance)

## Features

### 1. Data Extraction
The scraper extracts the following data from each listing:
- **Title**: Product title/name
- **Price**: Product price (supports multiple currencies)
- **URL**: Direct link to the listing
- **Image URL**: Primary image URL (first image found)
- **Description**: Product description or summary

### 2. Pagination Handling
- Automatically iterates through pages
- Detects 404 errors and stops scraping
- Checks for "no results" messages
- Configurable maximum page limit (default: 10)

### 3. Error Handling
- Retry mechanism for failed requests
- Random delays between requests
- User agent rotation
- Graceful handling of parsing errors

## API Endpoints

The following endpoints are available for the Todocoleccion scraper:

### 1. Test Scraper
```
GET /api/test-todocoleccion-scraper
```
Tests the scraper with sample keywords from the database.

### 2. Run Scraper
```
POST /api/run-todocoleccion-scraper
```
Runs the scraper with all keywords from the database.

### 3. Scraper Status
```
GET /api/todocoleccion-status
```
Returns the current status of the Todocoleccion scraper.

### 4. Scrape Specific Keyword
```
GET /api/scrape-todocoleccion/<keyword>
```
Scrapes a specific keyword (URL encoded).

## Usage Examples

### Using the API

1. **Test the scraper:**
   ```bash
   curl http://localhost:5000/api/test-todocoleccion-scraper
   ```

2. **Run the scraper:**
   ```bash
   curl -X POST http://localhost:5000/api/run-todocoleccion-scraper
   ```

3. **Check status:**
   ```bash
   curl http://localhost:5000/api/todocoleccion-status
   ```

4. **Scrape specific keyword:**
   ```bash
   curl "http://localhost:5000/api/scrape-todocoleccion/cigarro%20antiguo"
   ```

### Using the Scraper Directly

```python
from scrapers.todocoleccion_scraper import TodocoleccionScraper

# Create scraper instance
scraper = TodocoleccionScraper()

# Scrape a specific keyword
result = scraper.scrape_keyword("cigarro antiguo", max_pages=5)

print(f"Found {result['total_listings_found']} listings")
print(f"Saved {result['saved_listings']} listings")
print(f"Scraped {result['pages_scraped']} pages")
```

## Testing

Run the test script to verify the scraper functionality:

```bash
cd backend
python test_todocoleccion_scraper.py
```

## Configuration

### Rate Limiting
The scraper includes built-in rate limiting:
- Random delays between requests (2-5 seconds)
- Exponential backoff for failed requests
- User agent rotation

### Selectors
The scraper uses multiple CSS selectors to find listings:
- `div.item`, `div.producto`, `div.listing`
- `div[class*="item"]`, `div[class*="product"]`
- `li.item`, `article`
- Fallback selectors for different page layouts

### Price Parsing
Supports multiple price formats:
- Euro: `€123.45`, `123,45€`
- Dollar: `$123.45`, `123.45$`
- Pound: `£123.45`, `123.45£`

## Error Handling

The scraper handles various error scenarios:

1. **Network Errors**: Retries with exponential backoff
2. **404 Errors**: Stops pagination gracefully
3. **No Results**: Detects empty result pages
4. **Parsing Errors**: Continues with next listing
5. **Database Errors**: Logs but continues processing

## Logging

The scraper provides detailed logging:
- Page-by-page progress
- Number of listings found
- Error messages
- Success/failure counts

## Dependencies

Required packages (already in requirements.txt):
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `fake-useragent`: User agent rotation
- `lxml`: XML/HTML parser

## Database Schema

The scraper saves data to the `scraped_listings` table with the following schema:

```sql
CREATE TABLE public.scraped_listings (
  id serial not null,
  title text not null,
  url text not null,
  price numeric(10, 2) null,
  image_url text null,
  description text null,
  site text not null,
  keyword text not null,
  created_at timestamp without time zone null default now(),
  updated_at timestamp without time zone null default now(),
  constraint scraped_listings_pkey primary key (id),
  constraint scraped_listings_url_key unique (url)
);
```

The scraper automatically:
- Uses keywords from the `keywords` table
- Saves extracted data to the `scraped_listings` table
- Handles duplicate URL checking
- Sets appropriate timestamps

## Integration

The Todocoleccion scraper is automatically registered with the ScraperManager and can be used alongside other scrapers (eBay, etc.).

## Notes

- The scraper respects the website's robots.txt and terms of service
- Includes appropriate delays to avoid overwhelming the server
- Handles Spanish language content appropriately
- Supports both desktop and mobile user agents 