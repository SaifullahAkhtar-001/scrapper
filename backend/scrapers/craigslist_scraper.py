import re
import json
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import requests
from .base_scraper import BaseScraper
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
import logging

class CraigslistScraper(BaseScraper):
    """
    Enhanced scraper for searchcraigslist.net with improved error handling and performance
    """
    def __init__(self):
        super().__init__("craigslist")
        self.base_url = "https://searchcraigslist.net/results"
        self.cse_id = "008732268318596706411:nhtd4cwl5xu"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def minimal_wait(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """FIXED: Add the missing minimal_wait method"""
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build the search URL for the frontend"""
        clean_keyword = quote_plus(keyword)
        return f"{self.base_url}?q={clean_keyword}#gsc.tab=0&gsc.q={clean_keyword}&gsc.page={page}"

    def get_optimized_chrome_options(self) -> Options:
        """Get optimized Chrome options for better performance and stability"""
        chrome_options = Options()
        
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--window-size=1366,768")
        user_agent = self.get_random_user_agent()
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Performance/Stealth arguments
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-tools')
        
        # Exclude automation switches
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # FIXED: Use the correct property for pageLoadStrategy
        chrome_options.page_load_strategy = 'eager'
        
        return chrome_options

    def get_random_user_agent(self):
        """Get a random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)

    def get_rendered_html_optimized(self, url: str, timeout: int = 20) -> Optional[str]:
        """Get rendered HTML with improved error handling and proper timeout management"""
        driver = None
        try:
            self.logger.info(f"Loading page with Selenium: {url}")
            chrome_options = self.get_optimized_chrome_options()
            
            # Using Service object is best practice for managing the driver
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # FIXED: Add script to remove webdriver detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            
            # Wait for the Google CSE results container to be present
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".gsc-results-wrapper-visible, .gsc-resultsbox-visible, .gsc-webResult"))
                )
                self.logger.info("Google CSE container found")
            except TimeoutException:
                self.logger.warning("Timeout waiting for CSE container, continuing anyway")
            
            # Additional wait for results to populate
            time.sleep(3)

            html = driver.page_source
            self.logger.info(f"Successfully loaded page, HTML length: {len(html)}")
            
            # FIXED: Better detection of Google CSE content
            cse_indicators = ['gsc-', 'gs-', 'gsc-webResult', 'gs-webResult']
            has_cse_content = any(indicator in html for indicator in cse_indicators)
            
            if not has_cse_content:
                self.logger.warning("Google CSE content might be missing from the loaded HTML.")
            
            return html
            
        except TimeoutException:
            self.logger.error(f"Timeout loading page or finding CSE element: {url}")
            return None
        except WebDriverException as e:
            self.logger.error(f"WebDriver error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in get_rendered_html_optimized: {e}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    self.logger.error(f"Error closing driver: {e}")

    def try_requests_fallback(self, url: str) -> Optional[str]:
        """
        FIXED: Improved fallback to requests with better error handling
        """
        try:
            self.logger.info("Trying requests fallback...")
            
            # Create a session for better connection reuse
            session = requests.Session()
            session.headers.update(self.headers)
            
            # FIXED: Add retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = session.get(url, timeout=10)
                    if response.status_code == 200:
                        self.logger.info(f"Requests fallback successful on attempt {attempt + 1}")
                        return response.text
                    else:
                        self.logger.warning(f"Requests fallback attempt {attempt + 1} failed: Status {response.status_code}")
                except requests.RequestException as e:
                    self.logger.warning(f"Requests attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            return None
            
        except Exception as e:
            self.logger.error(f"Requests fallback failed: {e}")
            return None



    def extract_listings_from_page(self, html_content: str, keyword: str) -> List[Dict[str, Any]]:
        """Extract listings from HTML page - implementation of abstract method"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = []
        
        # FIXED: More comprehensive selectors for Google CSE results
        selectors = [
            '.gsc-webResult.gsc-result',
            '.gsc-webResult', 
            '.gs-webResult.gs-result',
            '.gs-webResult',
            '.gsc-result',
            '.gs-result',
            '[data-lpage]',
            '.gsc-control-cse .gsc-result',
            '.gsc-resultsbox-visible .gsc-webResult'
        ]
        
        results = []
        for selector in selectors:
            results = soup.select(selector)
            if results:
                self.logger.info(f"Found {len(results)} results using selector: {selector}")
                break
        
        if not results:
            self.logger.warning("No Google CSE results found with any selector")
            # Check if page indicates no results
            no_results_indicators = [
                'No results found', 'No matches', 'did not match any documents',
                'Your search .* did not match'
            ]
            page_text = soup.get_text().lower()
            for indicator in no_results_indicators:
                if re.search(indicator.lower(), page_text):
                    self.logger.info(f"Page indicates no results: {indicator}")
                    return []
            return []
        
        for result in results:
            try:
                listing = self.parse_single_result(result, keyword)
                if listing:
                    listings.append(listing)
                    self.logger.debug(f"Successfully parsed listing: {listing['title'][:50]}...")
                    
            except Exception as e:
                self.logger.error(f"Error extracting listing: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(listings)} listings from {len(results)} results")
        return listings

    def parse_single_result(self, result, keyword: str) -> Optional[Dict[str, Any]]:
        """FIXED: Parse a single Google CSE result with better error handling"""
        try:
            # Extract title and URL with multiple fallback strategies
            title_elem = result.select_one('.gs-title a, .gsc-title a, .gs-title, .gsc-title, h3 a, .r a')
            if not title_elem:
                self.logger.debug("No title element found")
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                self.logger.debug("Empty title found")
                return None
            
            # Get URL - try multiple approaches
            url = None
            if title_elem.name == 'a':
                url = title_elem.get('href')
            
            # If no URL in title element, look elsewhere
            if not url:
                url_elem = result.select_one('a[href*="craigslist"]')
                if url_elem:
                    url = url_elem.get('href')
            
            # If still no URL, try any link
            if not url:
                url_elem = result.select_one('a[href]')
                if url_elem:
                    url = url_elem.get('href')
            
            if not url:
                self.logger.debug("No URL found")
                return None
            
            # FIXED: Better Craigslist URL validation with more flexible checking
            craigslist_domains = ['craigslist.org', 'craigslist.com', 'craigslist.net']
            is_craigslist_url = any(domain in url.lower() for domain in craigslist_domains)
            
            if not is_craigslist_url:
                self.logger.debug(f"URL is not from Craigslist: {url}")
                return None
            
            # Extract description
            desc_selectors = [
                '.gs-snippet', '.gsc-snippet', 
                '.gs-content', '.gsc-content',
                '.st',  # Google search snippet class
                '.gs-bidi-start-align.gs-snippet'
            ]
            
            description = ""
            for selector in desc_selectors:
                desc_elem = result.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            # Extract image (if available)
            image_url = None
            img_selectors = [
                '.gs-image img',
                '.gsc-thumbnail img', 
                'img.gs-image',
                'img'
            ]
            
            for selector in img_selectors:
                img_elem = result.select_one(selector)
                if img_elem and img_elem.get('src'):
                    src = img_elem.get('src')
                    # Only include valid image URLs
                    if src and src.startswith(('http', 'data:', '//')) and not src.endswith('.gif'):
                        image_url = src
                        break
            
            # Clean title
            title = self.clean_title(title)
            
            # Extract price
            price = self.extract_price(f"{title} {description}")
            
            listing = {
                'title': title,
                'url': url,
                'image_url': image_url,
                'description': description,
                'site': 'craigslist',
                'keyword': keyword,
                'price': price
            }
            
            self.logger.debug(f"Successfully parsed listing: {title[:30]}...")
            return listing
            
        except Exception as e:
            self.logger.error(f"Error parsing single result: {e}")
            return None

    def extract_listings_from_html(self, html: str, keyword: str = "") -> List[Dict[str, Any]]:
        """FIXED: Extract listings from HTML with improved keyword parameter handling"""
        return self.extract_listings_from_page(html, keyword)

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text with improved patterns"""
        if not text:
            return None
            
        try:
            # Enhanced price patterns
            price_patterns = [
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD|\$)',  # 1000 dollars
                r'price:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # price: $1000
                r'asking:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # asking: $1000
                r'\$(\d{1,6})',  # Simple $1000
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    price_str = matches[0].replace(',', '')
                    try:
                        price = float(price_str)
                        # Reasonable price range check
                        if 0.01 <= price <= 100000:
                            return price
                    except ValueError:
                        continue
                    
        except Exception:
            pass
        return None

    def clean_title(self, title: str) -> str:
        """Clean and normalize title text"""
        if not title:
            return ""
        
        # Remove HTML tags and decode entities
        title = re.sub(r'<[^>]+>', '', title)
        title = BeautifulSoup(title, 'html.parser').get_text()
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Remove common Craigslist suffixes
        suffixes_to_remove = [
            r'\s*-\s*craigslist.*$',
            r'\s*-\s*collectibles\s*-\s*by\s*owner.*$',
            r'\s*-\s*household\s*items\s*-\s*by\s*owner.*$',
            r'\s*-\s*antiques\s*-\s*by\s*owner.*$',
            r'\s*-\s*furniture\s*-\s*by\s*owner.*$',
            r'\s*-\s*general\s*for\s*sale\s*-\s*by\s*owner.*$',
            r'\s*-\s*.*\s*-\s*by\s*owner.*$',
            r'\s*-\s*sale$',
        ]
        
        for suffix_pattern in suffixes_to_remove:
            title = re.sub(suffix_pattern, '', title, flags=re.IGNORECASE)
        
        return title.strip()

    def scrape_keyword(self, keyword: str, max_pages: int = 3) -> Dict[str, Any]:
        """FIXED: Scrape keyword with improved error handling and performance"""
        self.logger.info(f"Starting to scrape '{keyword}' on {self.site_name}")
        
        total_listings = 0
        saved_listings = 0
        errors = 0
        page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 2
        
        # Reduce max_pages to avoid long processing times
        max_pages = min(max_pages, 3)
        
        while consecutive_empty_pages < max_consecutive_empty and page <= max_pages:
            try:
                search_url = self.build_search_url(keyword, page)
                self.logger.info(f"Scraping page {page}: {search_url}")
                
                # Try Selenium first with improved error handling
                rendered_html = self.get_rendered_html_optimized(search_url, timeout=15)
                
                if not rendered_html:
                    self.logger.warning("Selenium failed, trying requests fallback...")
                    rendered_html = self.try_requests_fallback(search_url)
                
                if not rendered_html:
                    self.logger.error(f"Failed to load page {page}")
                    errors += 1
                    consecutive_empty_pages += 1
                    page += 1
                    continue
                
                # FIXED: Pass keyword parameter to extract function
                listings = self.extract_listings_from_html(rendered_html, keyword)
                total_listings += len(listings)
                

                
                if len(listings) == 0:
                    self.logger.warning(f"No listings found on page {page} (consecutive empty: {consecutive_empty_pages + 1})")
                    consecutive_empty_pages += 1
                    
                    # Debug: Check if we have any Google CSE content at all
                    cse_indicators = ['gsc-', 'gs-', 'gsc-webResult', 'gs-webResult']
                    has_cse_content = any(indicator in rendered_html.lower() for indicator in cse_indicators)
                    
                    if has_cse_content:
                        self.logger.info("Google CSE elements found in HTML but no listings extracted")
                    else:
                        self.logger.warning("No Google CSE elements found in HTML")
                    
                else:
                    self.logger.info(f"Found {len(listings)} listings on page {page}")
                    consecutive_empty_pages = 0
                    
                    # Save each listing
                    for listing in listings:
                        try:
                            self.save_listing(listing)
                            saved_listings += 1
                        except Exception as e:
                            self.logger.error(f"Error saving listing: {e}")
                            errors += 1
                
                page += 1
                
                # Short delay between pages
                if page <= max_pages:
                    self.minimal_wait(2, 3)  # Slightly increased delay
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page} for keyword '{keyword}': {e}")
                errors += 1
                consecutive_empty_pages += 1
                page += 1
                
                # Stop if too many errors
                if errors > 3:
                    self.logger.error("Too many errors, stopping scrape")
                    break
        
        # Final summary
        self.logger.info(f"Scraping completed for keyword: {keyword}")
        self.logger.info(f"Total listings found: {total_listings}")
        self.logger.info(f"Saved listings: {saved_listings}")
        self.logger.info(f"Errors: {errors}")
        self.logger.info(f"Pages scraped: {page - 1}")
        
        return {
            'keyword': keyword,
            'site': self.site_name,
            'total_listings_found': total_listings,
            'saved_listings': saved_listings,
            'errors': errors,
            'pages_scraped': page - 1
        }