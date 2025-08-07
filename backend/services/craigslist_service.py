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

class CraigslistService:
    @staticmethod
    def run_complete_scraping() -> Dict[str, Any]:
        """
        Run complete scraping for all keywords with optimized performance
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('craigslist_scraper.log')
            ]
        )
        logger = logging.getLogger(__name__)
        
        start_time = datetime.now()
        logger.info(f"Starting optimized Craigslist scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Get all keywords from database
            keywords = scraper_manager.get_keywords()
            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database. Please add some keywords first.',
                    'total_runtime': 0
                }
            
            # Get the Craigslist scraper
            craigslist_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'craigslist':
                    craigslist_scraper = scraper
                    break
            
            if not craigslist_scraper:
                return {
                    'success': False,
                    'error': 'Craigslist scraper not found in scraper manager',
                    'total_runtime': 0
                }
            
            logger.info(f"Found {len(keywords)} keywords to process")
            print(f"Keywords: {', '.join(keywords)}")
            print("-" * 80)
            
            # Initialize tracking variables
            total_results = {
                'keywords_processed': 0,
                'keywords_successful': 0,
                'keywords_failed': 0,
                'total_listings_found': 0,
                'total_listings_saved': 0,
                'total_pages_scraped': 0,
                'total_errors': 0,
                'keyword_results': []
            }
            
            # Process each keyword with optimized settings
            for i, keyword in enumerate(keywords, 1):
                keyword_start_time = datetime.now()
                logger.info(f"[{i}/{len(keywords)}] Processing keyword: '{keyword}'")
                print(f"\n[{i}/{len(keywords)}] Processing keyword: '{keyword}'")
                print("-" * 40)
                
                try:
                    # Use reduced page limit for faster processing (2 pages max)
                    result = craigslist_scraper.scrape_keyword(keyword, max_pages=2)
                    
                    # Update totals
                    total_results['keywords_processed'] += 1
                    if result['total_listings_found'] > 0:
                        total_results['keywords_successful'] += 1
                        total_results['total_listings_found'] += result['total_listings_found']
                        total_results['total_listings_saved'] += result['saved_listings']
                        total_results['total_pages_scraped'] += result['pages_scraped']
                        total_results['total_errors'] += result['errors']
                    else:
                        total_results['keywords_failed'] += 1
                    
                    # Store individual keyword result
                    keyword_result = {
                        'keyword': keyword,
                        'success': result['total_listings_found'] > 0,
                        'listings_found': result.get('total_listings_found', 0),
                        'listings_saved': result.get('saved_listings', 0),
                        'pages_scraped': result.get('pages_scraped', 0),
                        'errors': result.get('errors', 0),
                        'runtime': (datetime.now() - keyword_start_time).total_seconds(),
                        'error_message': result.get('error', None)
                    }
                    total_results['keyword_results'].append(keyword_result)
                    
                    # Print keyword summary
                    runtime = (datetime.now() - keyword_start_time).total_seconds()
                    if result['total_listings_found'] > 0:
                        print(f"✅ '{keyword}' completed successfully!")
                        print(f"   📊 Found: {result['total_listings_found']} listings")
                        print(f"   💾 Saved: {result['saved_listings']} listings")
                        print(f"   📄 Pages: {result['pages_scraped']} pages")
                        print(f"   ⏱️  Time: {runtime:.1f} seconds")
                        if result['errors'] > 0:
                            print(f"   ⚠️  Errors: {result['errors']}")
                        logger.info(f"Keyword '{keyword}' completed: {result['saved_listings']} saved")
                    else:
                        print(f"❌ '{keyword}' failed or found no results.")
                        print(f"   ⏱️  Time: {runtime:.1f} seconds")
                        logger.warning(f"Keyword '{keyword}' failed: {result}")
                    
                    # Reduced delay between keywords for faster processing
                    if i < len(keywords):
                        delay = 2  # Reduced from 3 to 2 seconds
                        print(f"   ⏸️  Waiting {delay} seconds before next keyword...")
                        time.sleep(delay)
                        
                except Exception as e:
                    total_results['keywords_processed'] += 1
                    total_results['keywords_failed'] += 1
                    logger.error(f"Error processing '{keyword}': {str(e)}")
                    
                    error_result = {
                        'keyword': keyword,
                        'success': False,
                        'listings_found': 0,
                        'listings_saved': 0,
                        'pages_scraped': 0,
                        'errors': 1,
                        'runtime': (datetime.now() - keyword_start_time).total_seconds(),
                        'error_message': str(e)
                    }
                    total_results['keyword_results'].append(error_result)
                    print(f"❌ Error processing '{keyword}': {str(e)}")
            
            # Calculate total runtime
            end_time = datetime.now()
            total_runtime = (end_time - start_time).total_seconds()
            
            # Print final summary
            print("\n" + "=" * 80)
            print("OPTIMIZED SCRAPING SUMMARY")
            print("=" * 80)
            print(f"🕒 Total Runtime: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")
            print(f"📝 Keywords Processed: {total_results['keywords_processed']}")
            print(f"✅ Keywords Successful: {total_results['keywords_successful']}")
            print(f"❌ Keywords Failed: {total_results['keywords_failed']}")
            print(f"📊 Total Listings Found: {total_results['total_listings_found']}")
            print(f"💾 Total Listings Saved: {total_results['total_listings_saved']}")
            print(f"📄 Total Pages Scraped: {total_results['total_pages_scraped']}")
            print(f"⚠️  Total Errors: {total_results['total_errors']}")
            
            # Performance metrics
            avg_time_per_keyword = total_runtime / len(keywords) if keywords else 0
            success_rate = (total_results['keywords_successful'] / total_results['keywords_processed']) * 100 if total_results['keywords_processed'] > 0 else 0
            print(f"⚡ Average Time per Keyword: {avg_time_per_keyword:.1f} seconds")
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            print("\n📋 Individual Keyword Results:")
            for result in total_results['keyword_results']:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {result['keyword']}: {result['listings_saved']} saved / {result['listings_found']} found ({result['pages_scraped']} pages, {result['runtime']:.1f}s)")
                if not result['success'] and result['error_message']:
                    print(f"      Error: {result['error_message']}")
            
            logger.info(f"Scraping completed successfully in {total_runtime:.1f} seconds")
            
            return {
                'success': True,
                'message': 'Optimized Craigslist scraping finished',
                'total_runtime': total_runtime,
                'summary': total_results,
                'performance_metrics': {
                    'avg_time_per_keyword': avg_time_per_keyword,
                    'success_rate': success_rate,
                    'total_keywords': len(keywords)
                }
            }
            
        except Exception as e:
            total_runtime = (datetime.now() - start_time).total_seconds()
            error_msg = f"Fatal error during Craigslist scraping: {str(e)}"
            logger.error(error_msg)
            print(f"\n❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'total_runtime': total_runtime
            }

if __name__ == "__main__":
    result = CraigslistService.run_complete_scraping()
    print("\nCraigslist Scraper Run Result:")
    import pprint
    pprint.pprint(result)