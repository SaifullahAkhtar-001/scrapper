from typing import List, Dict, Any
from .base_scraper import BaseScraper
from .ebay_scraper import EbayScraper
from .todocoleccion_scraper import TodocoleccionScraper
from .craigslist_scraper import CraigslistScraper
import time

class ScraperManager:
    """
    Manages multiple scrapers and provides a unified interface to run them.
    """
    
    def __init__(self):
        self.scrapers: List[BaseScraper] = []
    
    def add_scraper(self, scraper: BaseScraper):
        """Add a scraper to the manager"""
        self.scrapers.append(scraper)
        print(f"Added {scraper.site_name} scraper")
    
    def get_keywords(self) -> List[str]:
        """Get all active keywords from database"""
        from config.supabase_client import supabase_client
        keywords_data = supabase_client.get_all_keywords()
        return [kw['keyword'] for kw in keywords_data]

    def get_spanish_keywords(self) -> List[str]:
        """Get all active keywords from database"""
        from config.supabase_client import supabase_client
        keywords_data = supabase_client.get_all_spanish_keywords()
        return [kw['spanishkeyword'] for kw in keywords_data]   
    def run_all_scrapers(self) -> Dict[str, Any]:
        """Run all registered scrapers sequentially"""
        if not self.scrapers:
            print("No scrapers registered!")
            return {'error': 'No scrapers registered'}
        
        # Get keywords from database
        keywords = self.get_keywords()
        if not keywords:
            print("No keywords found in database!")
            return {'error': 'No keywords found'}
        
        print(f"Starting scraping with {len(keywords)} keywords across {len(self.scrapers)} scrapers")
        
        all_results = []
        total_start_time = time.time()
        
        # Run each scraper
        for scraper in self.scrapers:
            print(f"\n{'='*50}")
            print(f"Running {scraper.site_name} scraper...")
            print(f"{'='*50}")
            
            try:
                result = scraper.run(keywords)
                all_results.append(result)
            except Exception as e:
                print(f"Error running {scraper.site_name} scraper: {e}")
                all_results.append({
                    'site': scraper.site_name,
                    'error': str(e),
                    'keywords_processed': 0,
                    'total_listings_saved': 0,
                    'total_errors': 1
                })
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # Calculate overall summary
        total_saved = sum(r.get('total_listings_saved', 0) for r in all_results)
        total_errors = sum(r.get('total_errors', 0) for r in all_results)
        successful_scrapers = len([r for r in all_results if 'error' not in r])
        
        overall_summary = {
            'total_scrapers': len(self.scrapers),
            'successful_scrapers': successful_scrapers,
            'keywords_processed': len(keywords),
            'total_listings_saved': total_saved,
            'total_errors': total_errors,
            'total_duration_seconds': total_duration,
            'scraper_results': all_results
        }
        
        # Print overall summary
        print(f"\n{'='*60}")
        print(f"OVERALL SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Scrapers run: {len(self.scrapers)}")
        print(f"Successful scrapers: {successful_scrapers}")
        print(f"Keywords processed: {len(keywords)}")
        print(f"Total listings saved: {total_saved}")
        print(f"Total errors: {total_errors}")
        print(f"Total duration: {total_duration:.1f} seconds")
        print(f"{'='*60}")
        
        return overall_summary

# Global scraper manager instance
scraper_manager = ScraperManager()

# Register the eBay scraper
ebay_scraper = EbayScraper()
scraper_manager.add_scraper(ebay_scraper)

# Register the Todocoleccion scraper
todocoleccion_scraper = TodocoleccionScraper()
scraper_manager.add_scraper(todocoleccion_scraper)

# Register the Craigslist scraper
craigslist_scraper = CraigslistScraper()
scraper_manager.add_scraper(craigslist_scraper) 