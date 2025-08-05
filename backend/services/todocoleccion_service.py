from typing import Dict, Any, List
from scrapers import scraper_manager

class TodocoleccionService:
    """Service class for Todocoleccion scraper operations and testing"""

    @staticmethod
    def test_todocoleccion_scraper() -> Dict[str, Any]:
        """Test Todocoleccion scraper with sample keywords"""
        try:
            keywords = scraper_manager.get_keywords()

            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database. Please add some keywords first.'
                }

            # Run Todocoleccion scraper with first 2 keywords for testing
            test_keywords = keywords[:2]

            print(f"Testing Todocoleccion scraper with keywords: {test_keywords}")

            # Get the Todocoleccion scraper
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not found'
                }

            # Run the scraper
            result = todocoleccion_scraper.run(test_keywords)

            return {
                'success': True,
                'message': 'Todocoleccion scraper test completed',
                'test_keywords': test_keywords,
                'result': result
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def run_todocoleccion_scraper() -> Dict[str, Any]:
        """Run only the Todocoleccion scraper"""
        try:
            # Get the Todocoleccion scraper
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not found'
                }

            # Get keywords
            keywords = scraper_manager.get_keywords()
            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database. Please add some keywords first.'
                }

            # Run the scraper
            result = todocoleccion_scraper.run(keywords)

            return {
                'success': True,
                'message': 'Todocoleccion scraper completed',
                'result': result
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def scrape_specific_keyword(keyword: str) -> Dict[str, Any]:
        """Scrape a specific keyword using Todocoleccion scraper"""
        try:
            # Get the Todocoleccion scraper
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not found'
                }

            # Run the scraper for the specific keyword
            result = todocoleccion_scraper.scrape_keyword(keyword)

            return {
                'success': True,
                'message': f'Todocoleccion scraper completed for keyword: {keyword}',
                'result': result
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_todocoleccion_status() -> Dict[str, Any]:
        """Get status of Todocoleccion scraper"""
        try:
            # Check if Todocoleccion scraper is registered
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not registered'
                }

            return {
                'success': True,
                'message': 'Todocoleccion scraper is ready',
                'scraper_name': todocoleccion_scraper.site_name,
                'base_url': todocoleccion_scraper.base_url
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 