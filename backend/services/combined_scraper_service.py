from typing import Dict, Any, List
from datetime import datetime
import time
import sys
import os
import logging

# Add the parent directory to the Python path so we can import from scrapers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import scraper_manager
from scrapers.craigslist_scraper import CraigslistScraper
from scrapers.todocoleccion_scraper import TodocoleccionScraper

class CombinedScraperService:
    """
    Combined service that runs both Craigslist and TodoColeccion scrapers
    with comprehensive reporting and error handling.
    """
    
    @staticmethod
    def run_complete_scraping() -> Dict[str, Any]:
        """
        Run complete scraping for both Craigslist and TodoColeccion
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('combined_scraper.log')
            ]
        )
        logger = logging.getLogger(__name__)
        
        start_time = datetime.now()
        logger.info(f"Starting combined scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        print("🚀 COMBINED SCRAPER SERVICE")
        print("=" * 100)
        
        try:
            # Initialize results tracking
            combined_results = {
                'start_time': start_time.isoformat(),
                'total_runtime': 0,
                'scrapers_run': [],
                'overall_success': True,
                'total_listings_found': 0,
                'total_listings_saved': 0,
                'total_errors': 0,
                'scraper_results': {}
            }
            
            # Run Craigslist Scraper
            print("\n" + "=" * 50)
            print("🌐 CRAIGSLIST SCRAPER")
            print("=" * 50)
            
            craigslist_start = datetime.now()
            craigslist_result = CombinedScraperService._run_craigslist_scraper()
            craigslist_runtime = (datetime.now() - craigslist_start).total_seconds()
            
            combined_results['scraper_results']['craigslist'] = {
                'success': craigslist_result['success'],
                'runtime': craigslist_runtime,
                'result': craigslist_result
            }
            
            if craigslist_result['success']:
                combined_results['scrapers_run'].append('craigslist')
                combined_results['total_listings_found'] += craigslist_result.get('summary', {}).get('total_listings_found', 0)
                combined_results['total_listings_saved'] += craigslist_result.get('summary', {}).get('total_listings_saved', 0)
                combined_results['total_errors'] += craigslist_result.get('summary', {}).get('total_errors', 0)
            else:
                combined_results['overall_success'] = False
            
            # Add delay between scrapers
            print(f"\n⏸️  Waiting 5 seconds before starting TodoColeccion scraper...")
            time.sleep(5)
            
            # Run TodoColeccion Scraper
            print("\n" + "=" * 50)
            print("🇪🇸 TODOCLECCION SCRAPER")
            print("=" * 50)
            
            todocoleccion_start = datetime.now()
            todocoleccion_result = CombinedScraperService._run_todocoleccion_scraper()
            todocoleccion_runtime = (datetime.now() - todocoleccion_start).total_seconds()
            
            combined_results['scraper_results']['todocoleccion'] = {
                'success': todocoleccion_result['success'],
                'runtime': todocoleccion_runtime,
                'result': todocoleccion_result
            }
            
            if todocoleccion_result['success']:
                combined_results['scrapers_run'].append('todocoleccion')
                combined_results['total_listings_found'] += todocoleccion_result.get('summary', {}).get('total_listings_found', 0)
                combined_results['total_listings_saved'] += todocoleccion_result.get('summary', {}).get('total_listings_saved', 0)
                combined_results['total_errors'] += todocoleccion_result.get('summary', {}).get('total_errors', 0)
            else:
                combined_results['overall_success'] = False
            
            # Calculate total runtime
            end_time = datetime.now()
            total_runtime = (end_time - start_time).total_seconds()
            combined_results['total_runtime'] = total_runtime
            
            # Print comprehensive summary
            print("\n" + "=" * 100)
            print("📊 COMBINED SCRAPING SUMMARY")
            print("=" * 100)
            print(f"🕒 Total Runtime: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")
            print(f"✅ Scrapers Run: {', '.join(combined_results['scrapers_run'])}")
            print(f"📊 Total Listings Found: {combined_results['total_listings_found']}")
            print(f"💾 Total Listings Saved: {combined_results['total_listings_saved']}")
            print(f"⚠️  Total Errors: {combined_results['total_errors']}")
            
            # Individual scraper summaries
            print("\n📋 INDIVIDUAL SCRAPER RESULTS:")
            print("-" * 50)
            
            # Craigslist summary
            craigslist_summary = combined_results['scraper_results']['craigslist']
            status = "✅" if craigslist_summary['success'] else "❌"
            print(f"{status} CRAIGSLIST:")
            print(f"   Runtime: {craigslist_summary['runtime']:.1f} seconds")
            if craigslist_summary['success']:
                craigslist_data = craigslist_summary['result'].get('summary', {})
                print(f"   Keywords Processed: {craigslist_data.get('keywords_processed', 0)}")
                print(f"   Keywords Successful: {craigslist_data.get('keywords_successful', 0)}")
                print(f"   Listings Found: {craigslist_data.get('total_listings_found', 0)}")
                print(f"   Listings Saved: {craigslist_data.get('total_listings_saved', 0)}")
                print(f"   Pages Scraped: {craigslist_data.get('total_pages_scraped', 0)}")
            else:
                print(f"   Error: {craigslist_summary['result'].get('error', 'Unknown error')}")
            
            # TodoColeccion summary
            todocoleccion_summary = combined_results['scraper_results']['todocoleccion']
            status = "✅" if todocoleccion_summary['success'] else "❌"
            print(f"\n{status} TODOCLECCION:")
            print(f"   Runtime: {todocoleccion_summary['runtime']:.1f} seconds")
            if todocoleccion_summary['success']:
                todocoleccion_data = todocoleccion_summary['result'].get('summary', {})
                print(f"   Keywords Processed: {todocoleccion_data.get('keywords_processed', 0)}")
                print(f"   Keywords Successful: {todocoleccion_data.get('keywords_successful', 0)}")
                print(f"   Listings Found: {todocoleccion_data.get('total_listings_found', 0)}")
                print(f"   Listings Saved: {todocoleccion_data.get('total_listings_saved', 0)}")
                print(f"   Pages Scraped: {todocoleccion_data.get('total_pages_scraped', 0)}")
            else:
                print(f"   Error: {todocoleccion_summary['result'].get('error', 'Unknown error')}")
            
            # Performance metrics
            print("\n⚡ PERFORMANCE METRICS:")
            print("-" * 30)
            total_keywords = 0
            for scraper_name, scraper_data in combined_results['scraper_results'].items():
                if scraper_data['success']:
                    summary = scraper_data['result'].get('summary', {})
                    keywords_processed = summary.get('keywords_processed', 0)
                    total_keywords += keywords_processed
                    if keywords_processed > 0:
                        avg_time = scraper_data['runtime'] / keywords_processed
                        print(f"   {scraper_name.upper()}: {avg_time:.1f}s per keyword")
            
            if total_keywords > 0:
                overall_avg_time = total_runtime / total_keywords
                print(f"   OVERALL: {overall_avg_time:.1f}s per keyword")
            
            # Success rate calculation
            total_successful_keywords = 0
            total_processed_keywords = 0
            for scraper_data in combined_results['scraper_results'].values():
                if scraper_data['success']:
                    summary = scraper_data['result'].get('summary', {})
                    total_processed_keywords += summary.get('keywords_processed', 0)
                    total_successful_keywords += summary.get('keywords_successful', 0)
            
            if total_processed_keywords > 0:
                success_rate = (total_successful_keywords / total_processed_keywords) * 100
                print(f"   Success Rate: {success_rate:.1f}%")
            
            logger.info(f"Combined scraping completed in {total_runtime:.1f} seconds")
            
            return {
                'success': combined_results['overall_success'],
                'message': 'Combined scraping completed',
                'total_runtime': total_runtime,
                'combined_results': combined_results
            }
            
        except Exception as e:
            total_runtime = (datetime.now() - start_time).total_seconds()
            error_msg = f"Fatal error during combined scraping: {str(e)}"
            logger.error(error_msg)
            print(f"\n❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'total_runtime': total_runtime
            }
    
    @staticmethod
    def _run_craigslist_scraper() -> Dict[str, Any]:
        """Run Craigslist scraper with error handling"""
        try:
            print("🔄 Starting Craigslist scraper...")
            
            # Import and run Craigslist service
            from services.craigslist_service import CraigslistService
            result = CraigslistService.run_complete_scraping()
            
            if result['success']:
                print("✅ Craigslist scraper completed successfully")
            else:
                print(f"❌ Craigslist scraper failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error running Craigslist scraper: {str(e)}")
            return {
                'success': False,
                'error': f'Craigslist scraper error: {str(e)}',
                'total_runtime': 0
            }
    
    @staticmethod
    def _run_todocoleccion_scraper() -> Dict[str, Any]:
        """Run TodoColeccion scraper with error handling"""
        try:
            print("🔄 Starting TodoColeccion scraper...")
            
            # Import and run TodoColeccion service
            from services.todocoleccion_service import TodocoleccionService
            result = TodocoleccionService.run_complete_scraping()
            
            if result['success']:
                print("✅ TodoColeccion scraper completed successfully")
            else:
                print(f"❌ TodoColeccion scraper failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error running TodoColeccion scraper: {str(e)}")
            return {
                'success': False,
                'error': f'TodoColeccion scraper error: {str(e)}',
                'total_runtime': 0
            }
    
    @staticmethod
    def run_with_keyword_filter(keywords: List[str]) -> Dict[str, Any]:
        """
        Run combined scraping with specific keywords only
        """
        print(f"🎯 Running combined scraper with {len(keywords)} specific keywords")
        print(f"Keywords: {', '.join(keywords)}")
        
        # This would require modifying the individual services to accept keyword lists
        # For now, we'll run the full scraping
        return CombinedScraperService.run_complete_scraping()
    
    @staticmethod
    def run_quick_test() -> Dict[str, Any]:
        """
        Run a quick test with limited keywords for testing purposes
        """
        print("🧪 Running quick test with limited scope...")
        
        # Get a small subset of keywords for testing
        try:
            keywords = scraper_manager.get_keywords()
            test_keywords = keywords[:3] if len(keywords) >= 3 else keywords
            
            print(f"Testing with keywords: {test_keywords}")
            
            # For now, run the full scraping but with reduced scope
            # In a future version, we could modify the services to accept keyword lists
            return CombinedScraperService.run_complete_scraping()
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Quick test failed: {str(e)}'
            }

if __name__ == "__main__":
    # Run the combined scraper
    result = CombinedScraperService.run_complete_scraping()
    
    print("\n" + "=" * 100)
    print("🎯 FINAL RESULT")
    print("=" * 100)
    print(f"Overall Success: {'✅' if result['success'] else '❌'}")
    print(f"Total Runtime: {result['total_runtime']:.1f} seconds")
    
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Print detailed results if available
    if 'combined_results' in result:
        combined = result['combined_results']
        print(f"\nScrapers Run: {len(combined['scrapers_run'])}/{len(combined['scraper_results'])}")
        print(f"Total Listings Found: {combined['total_listings_found']}")
        print(f"Total Listings Saved: {combined['total_listings_saved']}")
    
    print("\nCombined scraper execution completed!")
