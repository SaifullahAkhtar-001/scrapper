import time
import random
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from fake_useragent import UserAgent
from config.supabase_client import supabase_client

class BaseScraper(ABC):
    """
    Base class for all scrapers. Provides common functionality like:
    - Rate limiting and delays
    - Error handling and retries
    - Data standardization
    - Database operations
    """
    
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with headers and retry strategy"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_random_delay(self, min_delay: float = 2.0, max_delay: float = 5.0) -> float:
        """Get a random delay between requests to avoid detection"""
        return random.uniform(min_delay, max_delay)
    
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make a safe HTTP request with retries and error handling"""
        for attempt in range(max_retries):
            try:
                # Add random delay
                time.sleep(self.get_random_delay())
                
                # Update user agent for each request
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def standardize_price(self, price_str: str) -> Optional[float]:
        """Convert price string to float, handling various formats"""
        if not price_str:
            return None
            
        try:
            # Remove currency symbols and whitespace
            cleaned = ''.join(c for c in price_str if c.isdigit() or c in '.,')
            
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                # Format like "1,234.56" or "1.234,56"
                if cleaned.rfind('.') > cleaned.rfind(','):
                    cleaned = cleaned.replace(',', '')
                else:
                    cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Assume comma is decimal separator if no period
                cleaned = cleaned.replace(',', '.')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def clean_title(self, title: str) -> str:
        """Clean and standardize listing title"""
        if not title:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(title.split())
        
        # Remove common unwanted prefixes/suffixes
        unwanted = ['NEW', 'USED', 'VINTAGE', 'AUTHENTIC', 'ORIGINAL']
        for word in unwanted:
            cleaned = cleaned.replace(word, '').replace(word.lower(), '')
        
        return cleaned.strip()
    
    def save_listing(self, listing_data: Dict[str, Any]) -> bool:
        """Save listing to database with duplicate checking"""
        try:
            # Check if URL already exists
            if supabase_client.check_url_exists(listing_data['url']):
                print(f"Listing already exists: {listing_data['url']}")
                return False
            
            # Save to database
            result = supabase_client.save_listing(listing_data)
            if result:
                print(f"Saved listing: {listing_data['title'][:50]}...")
                return True
            else:
                print(f"Failed to save listing: {listing_data['title'][:50]}...")
                return False
                
        except Exception as e:
            print(f"Error saving listing: {e}")
            return False
    
    @abstractmethod
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build search URL for the specific site"""
        pass
    
    @abstractmethod
    def extract_listings_from_page(self, html_content: str, keyword: str) -> List[Dict[str, Any]]:
        """Extract listings from HTML page - must be implemented by each scraper"""
        pass
    
    def scrape_keyword(self, keyword: str, max_pages: int = 3) -> Dict[str, Any]:
        """Scrape a single keyword across multiple pages"""
        print(f"Starting to scrape '{keyword}' on {self.site_name}")
        
        total_listings = 0
        saved_listings = 0
        errors = 0
        
        for page in range(1, max_pages + 1):
            try:
                # Build search URL
                search_url = self.build_search_url(keyword, page)
                print(f"Scraping page {page}: {search_url}")
                
                # Fetch page
                response = self.safe_request(search_url)
                if not response:
                    print(f"Failed to fetch page {page} for keyword '{keyword}'")
                    errors += 1
                    continue
                
                # Extract listings
                listings = self.extract_listings_from_page(response.text, keyword)
                total_listings += len(listings)
                
                print(f"Found {len(listings)} listings on page {page}")
                
                # Save each listing
                for listing in listings:
                    if self.save_listing(listing):
                        saved_listings += 1
                
                # Check if we should continue to next page
                if len(listings) == 0:
                    print(f"No more listings found on page {page}, stopping")
                    break
                    
            except Exception as e:
                print(f"Error scraping page {page} for keyword '{keyword}': {e}")
                errors += 1
                continue
        
        return {
            'keyword': keyword,
            'site': self.site_name,
            'total_listings_found': total_listings,
            'saved_listings': saved_listings,
            'errors': errors,
            'pages_scraped': min(page, max_pages)
        }
    
    def run(self, keywords: List[str]) -> Dict[str, Any]:
        """Run scraper for multiple keywords"""
        print(f"Starting {self.site_name} scraper with {len(keywords)} keywords")
        
        results = []
        start_time = time.time()
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n--- Processing keyword {i}/{len(keywords)}: '{keyword}' ---")
            
            result = self.scrape_keyword(keyword)
            results.append(result)
            
            # Add delay between keywords
            if i < len(keywords):
                delay = self.get_random_delay(3.0, 7.0)
                print(f"Waiting {delay:.1f} seconds before next keyword...")
                time.sleep(delay)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Summary
        total_saved = sum(r['saved_listings'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        
        summary = {
            'site': self.site_name,
            'keywords_processed': len(keywords),
            'total_listings_saved': total_saved,
            'total_errors': total_errors,
            'duration_seconds': duration,
            'results': results
        }
        
        print(f"\n=== {self.site_name} Scraper Summary ===")
        print(f"Keywords processed: {len(keywords)}")
        print(f"Total listings saved: {total_saved}")
        print(f"Total errors: {total_errors}")
        print(f"Duration: {duration:.1f} seconds")
        
        return summary 