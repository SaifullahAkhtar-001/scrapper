import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from scrapers.ebay_scraper import EbayScraper
from scrapers import scraper_manager
from services.stopword_service import StopwordService

class EbayService:
    """
    eBay scraping service with keyword filtering, stopword filtering, 
    URL caching, and pagination support
    """
    
    def __init__(self):
        self.scraper = EbayScraper()
        self.stopword_service = StopwordService()
        self.logger = logging.getLogger(__name__)
        
    def run_complete_scraping(self, keywords: Optional[List[str]] = None, quick_test: bool = False) -> Dict[str, Any]:
        """
        Run complete eBay scraping with all optimizations
        """
        start_time = datetime.now()
        self.logger.info(f"Starting eBay scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize URL cache for duplicate checking optimization
        self.scraper.initialize_url_cache()
        
        # Get keywords if not provided
        if keywords is None:
            keywords = scraper_manager.get_keywords()
            if quick_test:
                # Use first 3 keywords for quick testing
                keywords = keywords[:3]
        
        self.logger.info(f"Processing {len(keywords)} keywords")
        
        # Initialize counters
        total_listings_found = 0
        total_listings_saved = 0
        total_pages_scraped = 0
        keywords_processed = 0
        keywords_successful = 0
        
        # Process each keyword
        for keyword_obj in keywords:
            keyword = keyword_obj.get('keyword', '') if isinstance(keyword_obj, dict) else str(keyword_obj)
            
            if not keyword:
                continue
                
            try:
                self.logger.info(f"Processing keyword: '{keyword}'")
                keywords_processed += 1
                
                # Scrape keyword with pagination
                keyword_results = self.scrape_keyword_with_pagination(keyword, quick_test)
                
                if keyword_results['success']:
                    keywords_successful += 1
                    total_listings_found += keyword_results['listings_found']
                    total_listings_saved += keyword_results['listings_saved']
                    total_pages_scraped += keyword_results['pages_scraped']
                    
                    self.logger.info(f"Keyword '{keyword}': {keyword_results['listings_found']} found, "
                                   f"{keyword_results['listings_saved']} saved, "
                                   f"{keyword_results['pages_scraped']} pages")
                else:
                    self.logger.warning(f"Failed to process keyword: '{keyword}' - {keyword_results.get('error', 'Unknown error')}")
                
                # Add delay between keywords to be respectful
                if not quick_test:
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error processing keyword '{keyword}': {e}")
                continue
        
        # Calculate final statistics
        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds()
        
        summary = {
            'success': keywords_successful > 0,
            'runtime': runtime,
            'keywords_processed': keywords_processed,
            'keywords_successful': keywords_successful,
            'total_listings_found': total_listings_found,
            'total_listings_saved': total_listings_saved,
            'total_pages_scraped': total_pages_scraped,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        self.logger.info(f"eBay scraping completed in {runtime:.1f} seconds")
        self.logger.info(f"Summary: {keywords_successful}/{keywords_processed} keywords successful, "
                        f"{total_listings_saved} listings saved")
        
        return {
            'success': summary['success'],
            'summary': summary,
            'error': None if summary['success'] else 'No keywords processed successfully'
        }
    
    def scrape_keyword_with_pagination(self, keyword: str, quick_test: bool = False) -> Dict[str, Any]:
        """
        Scrape a single keyword with pagination support
        """
        listings_found = 0
        listings_saved = 0
        pages_scraped = 0
        page = 1
        max_pages = 3 if quick_test else 50  # Limit pages for testing
        
        try:
            while page <= max_pages:
                self.logger.info(f"Scraping page {page} for keyword '{keyword}'")
                
                # Scrape the specific page
                page_results = self._scrape_single_page(keyword, page)
                pages_scraped += 1
                
                if not page_results or len(page_results) == 0:
                    self.logger.info(f"No more results found for keyword '{keyword}' on page {page}")
                    break
                
                # Process listings from this page
                page_listings_found = len(page_results)
                page_listings_saved = 0
                
                for listing in page_results:
                    try:
                        # Apply stopword filtering and save
                        if self.scraper.save_listing(listing):
                            page_listings_saved += 1
                    except Exception as e:
                        self.logger.error(f"Error saving listing: {e}")
                        continue
                
                listings_found += page_listings_found
                listings_saved += page_listings_saved
                
                self.logger.info(f"Page {page}: {page_listings_found} found, {page_listings_saved} saved")
                
                # Check if we should continue to next page
                if page_listings_found == 0:
                    self.logger.info(f"No listings found on page {page}, stopping pagination")
                    break
                
                # Add delay between pages
                if not quick_test:
                    time.sleep(1)
                
                page += 1
            
            return {
                'success': True,
                'listings_found': listings_found,
                'listings_saved': listings_saved,
                'pages_scraped': pages_scraped
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping keyword '{keyword}': {e}")
            return {
                'listings_found': 0,
                'listings_saved': 0,
                'pages_scraped': 0,
                'stopped_early': False,
                'error': str(e)
            }
    
    def _scrape_single_page(self, keyword: str, page: int) -> List[Dict[str, Any]]:
        """Scrape a single page for a keyword"""
        try:
            # Build search URL for specific page
            search_url = self.scraper.build_search_url(keyword, page)
            print(f"Scraping page {page}: {search_url}")
            
            # Fetch page
            response = self.scraper.safe_request(search_url)
            if not response:
                print(f"Failed to fetch page {page} for keyword '{keyword}'")
                return []
            
            # Extract listings from page
            listings = self.scraper.extract_listings_from_page(response.text, keyword)
            print(f"Found {len(listings)} listings on page {page}")
            
            return listings
            
        except Exception as e:
            print(f"Error scraping page {page} for keyword '{keyword}': {e}")
            return []
    
    def scrape_specific_keyword(self, keyword: str, max_pages: int = 5) -> Dict[str, Any]:
        """
        Scrape a specific keyword with custom page limit
        """
        self.logger.info(f"Scraping specific keyword: '{keyword}' (max {max_pages} pages)")
        
        # Initialize URL cache
        self.scraper.initialize_url_cache()
        
        # Use the pagination method
        result = self.scrape_keyword_with_pagination(keyword, quick_test=False)
        
        return {
            'success': result['success'],
            'keyword': keyword,
            'listings_found': result['listings_found'],
            'listings_saved': result['listings_saved'],
            'pages_scraped': min(result['pages_scraped'], max_pages),
            'error': result.get('error')
        }

    @staticmethod
    def get_service_info() -> Dict[str, Any]:
        """Get information about the eBay service"""
        return {
            'service_name': 'eBay Scraper Service',
            'site': 'ebay',
            'features': [
                'Keyword-based search',
                'Stopword filtering',
                'URL cache optimization',
                'Pagination support',
                'Result limit detection',
                '240 items per page'
            ],
            'url_structure': 'https://www.ebay.com/sch/i.html?_nkw={keyword}&_sacat=0&_from=R40&_ipg=240&_pgn={page}'
        }
