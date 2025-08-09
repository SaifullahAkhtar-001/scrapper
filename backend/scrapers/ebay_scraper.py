import re
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class EbayScraper(BaseScraper):
    """
    eBay scraper implementation using DOM-based parsing
    """
    
    def __init__(self):
        super().__init__("ebay")
        self.base_url = "https://www.ebay.com"
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build eBay search URL with exact structure from user requirements"""
        # Clean keyword for URL
        clean_keyword = keyword.replace(' ', '+')
        
        # eBay search URL structure: _nkw=keyword&_sacat=0&_from=R40&_ipg=240&_pgn=page
        return f"{self.base_url}/sch/i.html?_nkw={clean_keyword}&_sacat=0&_from=R40&_ipg=240&_pgn={page}"
    
    def extract_listings_from_page(self, html_content: str, keyword: str) -> List[Dict[str, Any]]:
        """Extract listings from eBay search results page using user-specified DOM structure"""
        listings = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for eBay's "no more results" message first
            if self._check_no_more_results(soup):
                self.logger.info("Reached eBay's result limit or no more results")
                return []
            
            # Use the exact DOM structure provided by user: <ul class="srp-results srp-list clearfix"><li>
            results_container = soup.find('ul', class_='srp-results srp-list clearfix')
            if not results_container:
                # Fallback to other possible containers
                results_container = soup.find('ul', class_=re.compile(r'srp-results'))
                if not results_container:
                    self.logger.warning("Could not find eBay results container")
                    return []
            
            # Find all <li> elements within the results container
            listing_elements = results_container.find_all('li', class_='s-card s-card--horizontal')
            if not listing_elements:
                # Fallback to any <li> elements
                listing_elements = results_container.find_all('li')
            
            self.logger.info(f"Found {len(listing_elements)} listings on page")
            
            if not listing_elements:
                # Final fallback: look for any item-related elements
                listing_elements = soup.find_all(['li', 'div'], class_=re.compile(r'item|listing|product|s-card'))
                self.logger.info(f"Fallback: Found {len(listing_elements)} potential listings")
            
            for element in listing_elements:
                try:
                    listing = self._extract_single_listing(element, keyword)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    self.logger.error(f"Error extracting listing: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(listings)} listings from page")
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
        
        return listings
    
    def _extract_single_listing(self, element, keyword: str) -> Dict[str, Any]:
        """Extract data from a single listing element"""
        try:
            # Extract title
            title = self._extract_title(element)
            if not title:
                return None
            
            # Extract price
            price = self._extract_price(element)
            
            # Extract URL
            url = self._extract_url(element)
            if not url:
                return None
            
            # Extract images
            images = self._extract_images(element)
            
            # Extract description
            description = self._extract_description(element)
            
            # Create listing data - match database schema
            listing_data = {
                'title': self.clean_title(title),
                'price': price,
                'url': url,
                'image_url': images[0] if images else None,  # Take first image as image_url
                'description': description,
                'site': self.site_name,
                'keyword': keyword,
                'created_at': None  # Will be set by database
            }
            
            return listing_data
            
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            return None
    
    def _extract_title(self, element) -> str:
        """Extract listing title"""
        # Try multiple selectors for title based on user's DOM structure
        title_selectors = [
            'div.s-card__title span.su-styled-text',  # From user's DOM
            'h3.s-item__title',
            'div.s-item__title span',
            '[data-testid="item-title"]',
            '.s-item__title',
            'h3[class*="title"]',
            'a[class*="title"]',
            'span[class*="title"]'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and title.lower() != 'shop on ebay':
                    return title
        
        # Fallback: look for any text that might be a title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'title'))
        if title_elem:
            return title_elem.get_text(strip=True)
        
        return ""
    
    def _extract_price(self, element) -> float:
        """Extract listing price"""
        # Try multiple selectors for price based on user's DOM structure
        price_selectors = [
            'span.su-styled-text.s-card__price',  # From user's DOM
            'span.s-item__price',
            '.s-item__price',
            '[data-testid="item-price"]',
            'span[class*="price"]',
            '.price'
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self.standardize_price(price_text)
                if price:
                    return price
        
        return None
    
    def _extract_url(self, element) -> str:
        """Extract listing URL"""
        # Try to find the main listing link based on user's DOM structure
        url_selectors = [
            'a.su-link',  # From user's DOM
            'a.image-treatment',  # From user's DOM
            'a.s-item__link',
            'a[data-testid="item-link"]',
            'a[href*="/itm/"]',
            'a[class*="link"]'
        ]
        
        for selector in url_selectors:
            link_elem = element.select_one(selector)
            if link_elem:
                url = link_elem.get('href')
                if url:
                    # Ensure it's a full URL
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = self.base_url + '/' + url
                    return url
        
        # Fallback: look for any link that might be the listing
        link_elem = element.find('a', href=re.compile(r'/itm/'))
        if link_elem:
            url = link_elem.get('href')
            if url:
                if url.startswith('/'):
                    url = self.base_url + url
                return url
        
        return ""
    
    def _extract_images(self, element) -> List[str]:
        """Extract listing images"""
        images = []
        
        # Try multiple selectors for images based on user's DOM structure
        img_selectors = [
            'img.s-card__image',  # From user's DOM
            'img.s-item__image-img',
            'img[data-testid="item-image"]',
            'img[class*="image"]',
            'img[src*="i.ebayimg.com"]'
        ]
        
        for selector in img_selectors:
            img_elem = element.select_one(selector)
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    # Ensure it's a full URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.ebay.com' + src
                    images.append(src)
                    break
        
        # Fallback: look for any img tag
        if not images:
            img_elem = element.find('img')
            if img_elem:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.ebay.com' + src
                    images.append(src)
        
        return images
    
    def _extract_description(self, element) -> str:
        """Extract listing description/snippet"""
        # Try multiple selectors for description based on user's DOM structure
        desc_selectors = [
            'div.s-card__subtitle span.su-styled-text',  # From user's DOM
            'div.s-item__subtitle',
            '.s-item__subtitle',
            '[data-testid="item-subtitle"]',
            'span[class*="subtitle"]',
            'div[class*="description"]'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                if description:
                    return description
        
        # Fallback: look for any text that might be a description
        desc_elem = element.find(['p', 'span', 'div'], class_=re.compile(r'desc|subtitle|summary'))
        if desc_elem:
            return desc_elem.get_text(strip=True)
        
        return ""
    
    def _check_no_more_results(self, soup) -> bool:
        """Check if eBay shows the 'no more results' message"""
        # Check for the specific message mentioned by user
        no_results_messages = [
            "We're unable to show you more than 10,000 results. Please refine your search to narrow your results.",
            "The userLocation city, state and zipcode were ignored because the zipcode is invalid or not supported for the country.",
            "No results found",
            "0 results"
        ]
        
        page_text = soup.get_text().lower()
        for message in no_results_messages:
            if message.lower() in page_text:
                return True
        
        # Also check for empty results container
        results_container = soup.find('ul', class_='srp-results srp-list clearfix')
        if results_container:
            listings = results_container.find_all('li')
            if len(listings) == 0:
                return True
        
        return False 