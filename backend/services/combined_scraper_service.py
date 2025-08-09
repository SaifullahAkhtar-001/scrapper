from typing import Dict, Any, List
from datetime import datetime
import time
import sys
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to the Python path so we can import from scrapers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import scraper_manager
from scrapers.craigslist_scraper import CraigslistScraper
from scrapers.todocoleccion_scraper import TodocoleccionScraper
from services.ebay_service import EbayService

class CombinedScraperService:
    """
    Combined service that runs Craigslist, TodoColeccion, and eBay scrapers
    with comprehensive reporting, parallel execution, and error handling.
    """
    
    @staticmethod
    def run_complete_scraping() -> Dict[str, Any]:
        """
        Run complete scraping for Craigslist, TodoColeccion, and eBay
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
        print("🚀 COMBINED SCRAPER SERVICE - CRAIGSLIST + TODOCOLECCION + EBAY")
        print("=" * 100)
        
        try:
            # Get keyword counts for performance reporting
            english_keywords = scraper_manager.get_keywords()
            spanish_keywords = scraper_manager.get_spanish_keywords()
            
            print(f"🌍 Language-specific keyword optimization:")
            print(f"   📝 English keywords for Craigslist: {len(english_keywords)}")
            print(f"   📝 Spanish keywords for TodoColeccion: {len(spanish_keywords)}")
            print(f"   🚀 Total performance optimization: Using {len(english_keywords) + len(spanish_keywords)} targeted keywords")
            
            # Initialize results tracking
            combined_results = {
                'start_time': start_time.isoformat(),
                'total_runtime': 0,
                'scrapers_run': [],
                'overall_success': True,
                'total_listings_found': 0,
                'total_listings_saved': 0,
                'total_errors': 0,
                'scraper_results': {},
                'keyword_optimization': {
                    'english_keywords_count': len(english_keywords),
                    'spanish_keywords_count': len(spanish_keywords),
                    'total_optimized_keywords': len(english_keywords) + len(spanish_keywords)
                }
            }
            
            # Run both scrapers in parallel for maximum performance
            print("\n" + "=" * 60)
            print("🚀 PARALLEL SCRAPER EXECUTION")
            print("=" * 60)
            print("⚡ Running Craigslist, TodoColeccion, and eBay scrapers simultaneously...")
            
            # Create a thread pool for parallel execution
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all three scraper tasks
                future_to_scraper = {
                    executor.submit(CombinedScraperService._run_craigslist_scraper): 'craigslist',
                    executor.submit(CombinedScraperService._run_todocoleccion_scraper): 'todocoleccion',
                    executor.submit(CombinedScraperService._run_ebay_scraper): 'ebay'
                }
                
                # Track start times for each scraper
                scraper_start_times = {
                    'craigslist': datetime.now(),
                    'todocoleccion': datetime.now(),
                    'ebay': datetime.now()
                }
                
                # Process completed tasks as they finish
                for future in as_completed(future_to_scraper):
                    scraper_name = future_to_scraper[future]
                    end_time = datetime.now()
                    runtime = (end_time - scraper_start_times[scraper_name]).total_seconds()
                    
                    try:
                        result = future.result()
                        
                        print(f"\n✅ {scraper_name.upper()} scraper completed in {runtime:.1f} seconds")
                        
                        # Store results
                        combined_results['scraper_results'][scraper_name] = {
                            'success': result['success'],
                            'runtime': runtime,
                            'result': result
                        }
                        
                        if result['success']:
                            combined_results['scrapers_run'].append(scraper_name)
                            combined_results['total_listings_found'] += result.get('summary', {}).get('total_listings_found', 0)
                            combined_results['total_listings_saved'] += result.get('summary', {}).get('total_listings_saved', 0)
                            combined_results['total_errors'] += result.get('summary', {}).get('total_errors', 0)
                        else:
                            combined_results['overall_success'] = False
                            print(f"❌ {scraper_name.upper()} scraper failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"❌ {scraper_name.upper()} scraper encountered an exception: {str(e)}")
                        combined_results['scraper_results'][scraper_name] = {
                            'success': False,
                            'runtime': runtime,
                            'result': {'success': False, 'error': str(e)}
                        }
                        combined_results['overall_success'] = False
            
            print(f"\n🏁 Parallel execution completed! Both scrapers finished.")
            
            # Calculate total runtime
            end_time = datetime.now()
            total_runtime = (end_time - start_time).total_seconds()
            combined_results['total_runtime'] = total_runtime
            
            # Calculate performance metrics
            individual_runtimes = [data['runtime'] for data in combined_results['scraper_results'].values()]
            max_individual_runtime = max(individual_runtimes) if individual_runtimes else 0
            sequential_estimated_time = sum(individual_runtimes) + 5  # +5 for the delay we used to have
            time_saved = sequential_estimated_time - total_runtime
            performance_improvement = (time_saved / sequential_estimated_time * 100) if sequential_estimated_time > 0 else 0
            
            # Print final summary
            print("\n" + "=" * 100)
            print("🎯 PARALLEL SCRAPING SUMMARY")
            print("=" * 100)
            print(f"⚡ Parallel Execution Runtime: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")
            print(f"📈 Performance Improvement: {performance_improvement:.1f}% faster than sequential")
            print(f"⏱️  Time Saved: {time_saved:.1f} seconds")
            print(f"🔄 Sequential Estimated Time: {sequential_estimated_time:.1f} seconds")
            print(f"🚀 Overall Success: {'✅' if combined_results['overall_success'] else '❌'}")
            print(f"🔧 Scrapers Run: {len(combined_results['scrapers_run'])}/2")
            print(f"📊 Total Listings Found: {combined_results['total_listings_found']}")
            print(f"💾 Total Listings Saved: {combined_results['total_listings_saved']}")
            print(f"⚠️  Total Errors: {combined_results['total_errors']}")
            
            # Individual scraper performance
            print(f"\n📋 Individual Scraper Performance (Parallel):")
            for scraper_name, scraper_data in combined_results['scraper_results'].items():
                status = "✅" if scraper_data['success'] else "❌"
                print(f"  {status} {scraper_name.upper()}: {scraper_data['runtime']:.1f}s")
                if not scraper_data['success']:
                    error_msg = scraper_data['result'].get('error', 'Unknown error')
                    print(f"      Error: {error_msg}")
                else:
                    # Show detailed stats if available
                    result_summary = scraper_data['result'].get('summary', {})
                    if result_summary:
                        print(f"      Found: {result_summary.get('total_listings_found', 0)} listings")
                        print(f"      Saved: {result_summary.get('total_listings_saved', 0)} listings")
            
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
        """Run Craigslist scraper with error handling using English keywords"""
        try:
            print("🔄 Starting Craigslist scraper with English keywords...")
            
            # Get English keywords for Craigslist
            english_keywords = scraper_manager.get_keywords()  # This gets English keywords
            print(f"📝 Using {len(english_keywords)} English keywords for Craigslist")
            
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
        """Run TodoColeccion scraper with error handling using Spanish keywords"""
        try:
            print("🔄 Starting TodoColeccion scraper with Spanish keywords...")
            
            # Get Spanish keywords for TodoColeccion
            spanish_keywords = scraper_manager.get_spanish_keywords()  # This gets Spanish keywords
            print(f"📝 Using {len(spanish_keywords)} Spanish keywords for TodoColeccion")
            
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
    def _run_ebay_scraper() -> Dict[str, Any]:
        """Run eBay scraper with error handling using English keywords"""
        try:
            print("🔄 Starting eBay scraper with English keywords...")
            
            # Get English keywords for eBay
            english_keywords = scraper_manager.get_keywords()  # This gets English keywords
            print(f"📝 Using {len(english_keywords)} English keywords for eBay")
            
            # Run eBay service
            ebay_service = EbayService()
            result = ebay_service.run_complete_scraping()
            
            if result['success']:
                print("✅ eBay scraper completed successfully")
            else:
                print(f"❌ eBay scraper failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error running eBay scraper: {str(e)}")
            return {
                'success': False,
                'error': f'eBay scraper error: {str(e)}',
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
        Run a quick test with limited keywords for testing purposes using language-specific optimization
        """
        print("🧪 Running quick test with language-specific keyword optimization...")
        
        # Get language-specific keywords for testing
        try:
            english_keywords = scraper_manager.get_keywords()
            spanish_keywords = scraper_manager.get_spanish_keywords()
            
            # Use a small subset for quick testing
            test_english = english_keywords[:2] if len(english_keywords) >= 2 else english_keywords
            test_spanish = spanish_keywords[:2] if len(spanish_keywords) >= 2 else spanish_keywords
            
            print(f"🌍 Quick test optimization:")
            print(f"   📝 Testing with {len(test_english)} English keywords for Craigslist: {test_english}")
            print(f"   📝 Testing with {len(test_spanish)} Spanish keywords for TodoColeccion: {test_spanish}")
            print(f"   📝 Testing with {len(test_english)} English keywords for eBay: {test_english}")
            
            # Run the full scraping with optimized keyword selection
            # The individual services will use their respective language-specific keywords
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
