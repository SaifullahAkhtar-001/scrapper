#!/usr/bin/env python3
"""
eBay Scraper Test Runner

This script tests the new eBay scraper integration with all optimizations:
- Stopword filtering
- URL cache optimization  
- Keyword-based search
- Pagination with result limit detection
- Integration with existing database schema

Usage:
    python run_ebay_scraper.py [--quick-test] [--keyword "test keyword"]
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ebay_service import EbayService
from services.combined_scraper_service import CombinedScraperService

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ebay_scraper_test.log')
        ]
    )
    return logging.getLogger(__name__)

def test_ebay_scraper_standalone(keyword: str = None):
    """Test eBay scraper as standalone service"""
    logger = setup_logging()
    
    print("=" * 80)
    print("🛒 EBAY SCRAPER STANDALONE TEST")
    print("=" * 80)
    
    try:
        ebay_service = EbayService()
        
        if keyword:
            print(f"🎯 Testing with specific keyword: '{keyword}'")
            result = ebay_service.scrape_specific_keyword(keyword, max_pages=2)
        else:
            print("🔄 Running complete eBay scraping with all keywords...")
            result = ebay_service.run_complete_scraping(quick_test=True)
        
        # Display results
        if result['success']:
            print("\n✅ eBay scraper test PASSED!")
            if 'summary' in result:
                summary = result['summary']
                print(f"📊 Results Summary:")
                print(f"   ⏱️  Runtime: {summary.get('runtime', 0):.1f} seconds")
                print(f"   📝 Keywords processed: {summary.get('keywords_processed', 0)}")
                print(f"   ✅ Keywords successful: {summary.get('keywords_successful', 0)}")
                print(f"   📦 Listings found: {summary.get('total_listings_found', 0)}")
                print(f"   💾 Listings saved: {summary.get('total_listings_saved', 0)}")
                print(f"   📄 Pages scraped: {summary.get('total_pages_scraped', 0)}")
            else:
                print(f"📦 Listings found: {result.get('listings_found', 0)}")
                print(f"💾 Listings saved: {result.get('listings_saved', 0)}")
        else:
            print(f"\n❌ eBay scraper test FAILED: {result.get('error', 'Unknown error')}")
        
        return result['success']
        
    except Exception as e:
        logger.error(f"Error during eBay scraper test: {e}")
        print(f"\n❌ Test failed with exception: {e}")
        return False

def test_ebay_integration():
    """Test eBay scraper integration in combined service"""
    logger = setup_logging()
    
    print("\n" + "=" * 80)
    print("🚀 EBAY INTEGRATION TEST - PARALLEL EXECUTION")
    print("=" * 80)
    
    try:
        print("🔄 Running combined scraper with eBay integration...")
        result = CombinedScraperService.run_quick_test()
        
        if result['success']:
            print("\n✅ eBay integration test PASSED!")
            
            # Check if eBay was included in the results
            combined_results = result.get('combined_results', {})
            scraper_results = combined_results.get('scraper_results', {})
            
            if 'ebay' in scraper_results:
                ebay_result = scraper_results['ebay']
                print(f"🛒 eBay scraper in parallel execution:")
                print(f"   ✅ Success: {ebay_result['success']}")
                print(f"   ⏱️  Runtime: {ebay_result['runtime']:.1f} seconds")
                
                if ebay_result['success']:
                    ebay_summary = ebay_result['result'].get('summary', {})
                    print(f"   📦 Listings found: {ebay_summary.get('total_listings_found', 0)}")
                    print(f"   💾 Listings saved: {ebay_summary.get('total_listings_saved', 0)}")
            else:
                print("⚠️  eBay scraper not found in parallel execution results")
                return False
        else:
            print(f"\n❌ eBay integration test FAILED: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error during eBay integration test: {e}")
        print(f"\n❌ Integration test failed with exception: {e}")
        return False

def display_ebay_service_info():
    """Display eBay service information"""
    print("\n" + "=" * 80)
    print("📋 EBAY SCRAPER SERVICE INFORMATION")
    print("=" * 80)
    
    info = EbayService.get_service_info()
    print(f"🏷️  Service: {info['service_name']}")
    print(f"🌐 Site: {info['site']}")
    print(f"🔗 URL Structure: {info['url_structure']}")
    print(f"✨ Features:")
    for feature in info['features']:
        print(f"   • {feature}")

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='eBay Scraper Test Runner')
    parser.add_argument('--quick-test', action='store_true', 
                       help='Run quick test with limited keywords')
    parser.add_argument('--keyword', type=str, 
                       help='Test with specific keyword')
    parser.add_argument('--integration-only', action='store_true',
                       help='Only test integration, skip standalone test')
    parser.add_argument('--standalone-only', action='store_true',
                       help='Only test standalone, skip integration test')
    
    args = parser.parse_args()
    
    print("🛒 eBay Scraper Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display service info
    display_ebay_service_info()
    
    test_results = []
    
    # Run standalone test
    if not args.integration_only:
        standalone_success = test_ebay_scraper_standalone(args.keyword)
        test_results.append(('Standalone eBay Scraper', standalone_success))
    
    # Run integration test
    if not args.standalone_only:
        integration_success = test_ebay_integration()
        test_results.append(('eBay Integration (Parallel)', integration_success))
    
    # Final results
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    all_passed = True
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
