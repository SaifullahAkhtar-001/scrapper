from typing import Dict, Any, List
from scrapers import scraper_manager

class ScraperService:
    """Service class for scraper operations and testing"""
    
    @staticmethod
    def get_scraper_status() -> Dict[str, Any]:
        """Get status of scraper system"""
        try:
            keywords = scraper_manager.get_keywords()
            registered_scrapers = [scraper.site_name for scraper in scraper_manager.scrapers]
            
            return {
                'success': True,
                'keywords_count': len(keywords),
                'keywords': keywords,
                'registered_scrapers': registered_scrapers,
                'scrapers_count': len(registered_scrapers),
                'message': 'Scraper system is ready' if registered_scrapers else 'No scrapers registered'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def test_ebay_scraper() -> Dict[str, Any]:
        """Test eBay scraper with sample keywords"""
        try:
            keywords = scraper_manager.get_keywords()
            
            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database. Please add some keywords first.'
                }
            
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
                return {
                    'success': False,
                    'error': 'eBay scraper not found'
                }
            
            # Run the scraper
            result = ebay_scraper.run(test_keywords)
            
            return {
                'success': True,
                'message': 'eBay scraper test completed',
                'test_keywords': test_keywords,
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def run_all_scrapers() -> Dict[str, Any]:
        """Run all registered scrapers"""
        try:
            result = scraper_manager.run_all_scrapers()
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            return {
                'success': True,
                'message': 'All scrapers completed',
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 