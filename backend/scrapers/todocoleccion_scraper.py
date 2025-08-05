import re
import os
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TodocoleccionScraper(BaseScraper):
    """
    Todocoleccion.net scraper implementation
    Handles pagination and extracts listings from search results
    Updated to properly target the correct DOM structure
    """
    
    def __init__(self):
        super().__init__("todocoleccion")
        self.base_url = "https://www.todocoleccion.net"
        # Create directory for saving soup content
        self.soup_output_dir = "soup_content"
        os.makedirs(self.soup_output_dir, exist_ok=True)
        
    def save_soup_content(self, content: str, filename: str, content_type: str = "page") -> str:
        """Save soup content to a file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = os.path.join(self.soup_output_dir, f"{timestamp}_{safe_filename}_{content_type}.html")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Saved {content_type} content to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving soup content: {e}")
            return ""
    
    def save_listing_soup_content(self, element, listing_id: str, keyword: str) -> str:
        """Save individual listing soup content"""
        try:
            soup_content = str(element)
            filename = f"listing_{listing_id}_{keyword}"
            return self.save_soup_content(soup_content, filename, "listing")
        except Exception as e:
            print(f"Error saving listing soup content: {e}")
            return ""
    
    def build_search_url(self, keyword: str, page: int = 1) -> str:
        """Build Todocoleccion search URL with pagination"""
        # Clean keyword for URL (encode spaces and special characters)
        clean_keyword = keyword.replace(' ', '%20')
        
        # Todocoleccion search URL structure
        # P=page_number, bu=search_term, O=rl (sort order - relevance/recent)
        return f"{self.base_url}/buscador?P={page}&bu={clean_keyword}&O=rl"
    
    def extract_listings_from_page(self, html_content: str, keyword: str) -> List[Dict[str, Any]]:
        """Extract listings from Todocoleccion search results page"""
        listings = []
        
        try:
            # Save the full page content
            page_filename = f"page_{keyword}"
            self.save_soup_content(html_content, page_filename, "full_page")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # First, try to find the main search results container
            search_container = soup.find('div', id='buscador-lote-items-container')
            if not search_container:
                print("Main search container not found, using full page")
                search_container = soup
            else:
                print("Found main search container")
            
            # print('search_containersearch_containersearch_containersearch_container',search_container)

            # Then look for the items list container within the search container
            items_container = search_container.find('div', class_='card-lotes-in-gallery')
            print('items_containeritems_containeritems_containeritems_container',items_container)
            if not items_container:
                # Fallback to any _lote_items container
                items_container = search_container.find('div', class_=lambda x: x and '_lote_items' in x)
                if not items_container:
                    items_container = search_container
                    print("Items container not found, using search container")
                else:
                    print("Found fallback items container")
            else:
                print("Found items list container")
            
            # Now find all individual listing items
            listing_elements = items_container.find_all('div', class_='card-lote card-lote-as-gallery')
            
            if not listing_elements:
                print("No listing elements found with class 'card-lote card-lote-as-gallery'")
                # Debug: show available div classes that might contain listings
                all_divs = items_container.find_all('div', class_=True)
                relevant_classes = set()
                for div in all_divs[:50]:  # Check first 50 divs
                    for class_name in div.get('class', []):
                        if any(keyword in class_name.lower() for keyword in ['item', 'lote', 'listing', 'product']):
                            relevant_classes.add(class_name)
                print(f"Relevant div classes found: {list(relevant_classes)}")
                return listings
            
            print(f"Found {len(listing_elements)} listing elements")
            
            for i, element in enumerate(listing_elements):
                try:
                    # Extract data-id-lote for debugging
                    lote_id = element.get('data-id-lote', 'unknown')
                    print(f"Processing listing {i+1}/{len(listing_elements)} (ID: {lote_id})")
                    
                    # Save individual listing soup content
                    self.save_listing_soup_content(element, lote_id, keyword)
                    
                    listing = self._extract_single_listing(element, keyword)
                    if listing:
                        listings.append(listing)
                        print(f"Successfully extracted listing: {listing['title'][:50]}...")
                    else:
                        print(f"Failed to extract listing {i+1}")
                except Exception as e:
                    print(f"Error extracting listing {i+1}: {e}")
                    continue
            
            print(f"Successfully extracted {len(listings)} listings from page")
            
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            import traceback
            traceback.print_exc()
        
        return listings
    
    def _extract_single_listing(self, element, keyword: str) -> Dict[str, Any]:
        """Extract data from a single listing element"""
        try:
            # Extract title - this is the most important field
            title = self._extract_title(element)
            if not title or len(title.strip()) < 3:
                print("No valid title found, skipping listing")
                return None
            
            # Extract price
            price = self._extract_price(element)
            
            # Extract URL
            url = self._extract_url(element)
            if not url:
                print("No URL found, skipping listing")
                return None
            
            # Extract images
            images = self._extract_images(element)
            
            # Extract description/category
            description = self._extract_description(element)
            
            # Extract seller information
            seller_info = self._extract_seller_info(element)
            
            # Extract auction/offer type
            # listing_type = self._extract_listing_type(element)
            
            # Create listing data - match database schema
            listing_data = {
                'title': self.clean_title(title),
                'price': price,
                'url': url,
                'image_url': images[0] if images else None,
                'description': description,
                'site': self.site_name,
                'keyword': keyword,
            }
            
            return listing_data
            
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_title(self, element) -> str:
        """Extract listing title using the correct DOM structure"""
        # Based on the HTML structure provided
        title_selectors = [
            'h2._lote_item-titulo a#lot-title-*',  # Primary selector with ID
            'h2._lote_item-titulo a.js-lot-titles',  # Primary selector with class
            'h2._lote_item-titulo a',  # Fallback without specific class
            'h2 a[title]',  # Any h2 with titled link
            'a[id^="lot-title-"]',  # Any link with lot-title ID
        ]
        
        for selector in title_selectors:
            if '*' in selector:
                # Handle wildcard selector manually
                title_elem = element.select_one('h2._lote_item-titulo a[id^="lot-title-"]')
            else:
                title_elem = element.select_one(selector)
            
            if title_elem:
                # First try to get the title attribute (full title)
                title_attr = title_elem.get('title')
                if title_attr and title_attr.strip():
                    return title_attr.strip()
                
                # Fallback to text content
                title_text = title_elem.get_text(strip=True)
                if title_text and len(title_text) > 3:
                    return title_text
        
        print("No title found with standard selectors")
        return ""
    
    def _extract_price(self, element) -> float:
        """Extract price using the correct DOM structure"""
        # Based on HTML structure: span.precio-lote-listado._lote_item-precio
        price_selectors = [
            'span.precio-lote-listado._lote_item-precio',  # Primary selector
            'span._lote_item-precio',  # Fallback
            'span[class*="precio-lote-listado"]',  # Partial match
            'span[class*="_lote_item-precio"]',  # Another partial match
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self.standardize_price(price_text)
                if price is not None:
                    return price
        
        # Fallback: search for any text containing currency
        text_content = element.get_text()
        price_patterns = [
            r'(\d+[.,]\d+)\s*€',  # Euro format: 12,00 €
            r'(\d+)\s*€',         # Simple euro: 12 €
            r'€\s*(\d+[.,]\d+)',  # Euro prefix
            r'(\d+[.,]\d+)\s*\$', # Dollar format
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text_content)
            if match:
                price = self.standardize_price(match.group(1))
                if price is not None:
                    return price
        
        return None
    
    def _extract_url(self, element) -> str:
        """Extract listing URL using the correct DOM structure"""
        # Same element that contains the title should have the URL
        url_selectors = [
            'h2._lote_item-titulo a[id^="lot-title-"]',  # Primary selector
            'h2._lote_item-titulo a.js-lot-titles',     # With class
            'h2._lote_item-titulo a',                   # Fallback
            'a[href*="/coleccionismo"]',                # Any collectibles link
            'a[href]',                                  # Any link as last resort
        ]
        
        for selector in url_selectors:
            link_elem = element.select_one(selector)
            if link_elem:
                url = link_elem.get('href')
                if url:
                    return self._normalize_url(url)
        
        print("No URL found with any selector")
        return ""
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure it's a full URL"""
        if not url:
            return ""
        
        # If it's already a full URL
        if url.startswith('http'):
            return url
        
        # If it starts with //, add https:
        if url.startswith('//'):
            return 'https:' + url
        
        # If it starts with /, add base URL
        if url.startswith('/'):
            return self.base_url + url
        
        # Otherwise, add base URL with /
        return self.base_url + '/' + url
    
    def _extract_images(self, element) -> List[str]:
        """Extract images using the correct DOM structure"""
        images = []
        
        # Based on HTML: a.ga-track-click-buscador._lote_item-img-main-link with data-image-url
        img_selectors = [
            'a._lote_item-img-main-link[data-image-url]',  # Primary selector
            'a[data-image-url]',                           # Any link with data-image-url
            'a._lote_item-img-main-link img',              # Image within link
            'img._lote_item-img-main',                     # Direct image
            'img[class*="thumb-lote-foto"]',               # Thumbnail image
        ]
        
        for selector in img_selectors:
            img_elem = element.select_one(selector)
            if img_elem:
                # For links, try to get data-image-url first
                if img_elem.name == 'a':
                    image_url = img_elem.get('data-image-url')
                    if image_url:
                        normalized_url = self._normalize_url(image_url)
                        if normalized_url:
                            images.append(normalized_url)
                            break
                
                # For img tags, get src
                elif img_elem.name == 'img':
                    src = img_elem.get('src') or img_elem.get('data-src')
                    if src and 'todocoleccion' in src:  # Ensure it's a valid image
                        normalized_url = self._normalize_url(src)
                        if normalized_url:
                            images.append(normalized_url)
                            break
        
        return images
    
    def _extract_description(self, element) -> str:
        """Extract category/description using the correct DOM structure"""
        # Based on HTML: p._lote_item-section a
        desc_selectors = [
            'p._lote_item-section a',  # Primary selector
            'p._lote_item-section',    # Without link
            'p[class*="_lote_item-section"]',  # Partial match
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                if description and len(description) > 5:
                    return description
        
        return ""
    
    def _extract_seller_info(self, element) -> str:
        """Extract seller information"""
        # Based on HTML: p.lote-vendedor span with seller name
        seller_selectors = [
            'p.lote-vendedor span[title*="Tienda"]',  # Store seller
            'p.lote-vendedor span[title*="Vendedor"]',  # Regular seller
            'p.lote-vendedor span.fs-14',  # Generic seller info
        ]
        
        for selector in seller_selectors:
            seller_elem = element.select_one(selector)
            if seller_elem:
                seller_text = seller_elem.get_text(strip=True)
                if seller_text:
                    return seller_text
        
        return ""
    
    def _extract_listing_type(self, element) -> str:
        """Extract whether it's auction, offers accepted, etc."""
        # Based on HTML: a._lote_item-img-footerbox with different classes
        type_selectors = [
            'a._lote_item-img-footerbox-subasta',  # Auction
            'a._lote_item-img-footerbox-admite_ofertas',  # Accepts offers
        ]
        
        for selector in type_selectors:
            type_elem = element.select_one(selector)
            if type_elem:
                return type_elem.get_text(strip=True)
        
        return "Venta directa"  # Direct sale as default
    
    def scrape_keyword(self, keyword: str, max_pages: int = 20) -> Dict[str, Any]:
        """Enhanced scraping with better error handling and pagination detection"""
        print(f"Starting to scrape '{keyword}' on {self.site_name}")
        
        # Save scraping session info
        session_info = f"Scraping session for keyword: {keyword}\nStarted at: {datetime.now()}\nMax pages: {max_pages}\n"
        self.save_soup_content(session_info, f"session_{keyword}", "session_info")
        
        total_listings = 0
        saved_listings = 0
        errors = 0
        page = 1
        consecutive_empty_pages = 0
        max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
        
        while page <= max_pages and consecutive_empty_pages < max_consecutive_empty:
            try:
                # Build search URL
                search_url = self.build_search_url(keyword, page)
                print(f"Scraping page {page}: {search_url}")
                
                # Fetch page
                response = self.safe_request(search_url)
                if not response:
                    print(f"Failed to fetch page {page} for keyword '{keyword}'")
                    errors += 1
                    consecutive_empty_pages += 1
                    page += 1
                    continue
                
                # Check for 404 or error pages
                if response.status_code == 404:
                    print(f"Page {page} returned 404 - reached end of results")
                    break
                
                # Check for common "no results" indicators
                response_text = response.text.lower()
                no_results_indicators = [
                    "no se encontraron resultados",
                    "no results found",
                    "sin resultados",
                    "no hay resultados",
                    "0 resultados"
                ]
                
                if any(indicator in response_text for indicator in no_results_indicators):
                    print(f"Page {page} indicates no results - reached end of pagination")
                    break
                
                # Extract listings
                listings = self.extract_listings_from_page(response.text, keyword)
                
                if len(listings) == 0:
                    consecutive_empty_pages += 1
                    print(f"No listings found on page {page} (consecutive empty: {consecutive_empty_pages})")
                else:
                    consecutive_empty_pages = 0  # Reset counter
                    total_listings += len(listings)
                    print(f"Found {len(listings)} listings on page {page}")
                    
                    # Save each listing
                    for listing in listings:
                        if self.save_listing(listing):
                            saved_listings += 1
                
                page += 1
                
                # Add small delay between requests to be respectful
                import time
                time.sleep(1)
                    
            except Exception as e:
                print(f"Error scraping page {page} for keyword '{keyword}': {e}")
                errors += 1
                consecutive_empty_pages += 1
                page += 1
                
                # Don't break immediately on single page errors
                if errors > 5:  # But break if too many errors
                    print("Too many errors, stopping scrape")
                    break
        
        # Save final session summary
        final_summary = f"""
Scraping session completed for keyword: {keyword}
Ended at: {datetime.now()}
Total listings found: {total_listings}
Saved listings: {saved_listings}
Errors: {errors}
Pages scraped: {page - 1}
        """
        self.save_soup_content(final_summary, f"session_{keyword}", "final_summary")
        
        return {
            'keyword': keyword,
            'site': self.site_name,
            'total_listings_found': total_listings,
            'saved_listings': saved_listings,
            'errors': errors,
            'pages_scraped': page - 1
        }