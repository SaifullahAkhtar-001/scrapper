#!/usr/bin/env python3
"""
Main scraper runner script.
This is the single command to run all scrapers.
Usage: python run_scraper.py
"""

import sys
import os
import time
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers import scraper_manager
from config.supabase_client import supabase_client

def main():
    """Main function to run all scrapers"""
    print("=" * 60)
    print("🚀 STARTING MULTI-SITE SCRAPER")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test database connection
        print("\n🔍 Testing database connection...")
        keywords = scraper_manager.get_keywords()
        if not keywords:
            print("❌ No keywords found in database!")
            print("Please add keywords to the 'keywords' table in Supabase")
            return 1
        
        print(f"✅ Database connected successfully")
        print(f"📝 Found {len(keywords)} keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        
        # Check if any scrapers are registered
        if not scraper_manager.scrapers:
            print("\n❌ No scrapers registered!")
            print("Please add scrapers to the scraper manager")
            print("Example: scraper_manager.add_scraper(EbayScraper())")
            return 1
        
        print(f"\n🔧 Registered scrapers: {len(scraper_manager.scrapers)}")
        for scraper in scraper_manager.scrapers:
            print(f"   - {scraper.site_name}")
        
        # Run all scrapers
        print(f"\n🎯 Starting scraping process...")
        results = scraper_manager.run_all_scrapers()
        
        # Check for errors
        if 'error' in results:
            print(f"\n❌ Scraping failed: {results['error']}")
            return 1
        
        # Success summary
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Final Results:")
        print(f"   - Scrapers run: {results['total_scrapers']}")
        print(f"   - Successful scrapers: {results['successful_scrapers']}")
        print(f"   - Keywords processed: {results['keywords_processed']}")
        print(f"   - Total listings saved: {results['total_listings_saved']}")
        print(f"   - Total errors: {results['total_errors']}")
        print(f"   - Duration: {results['total_duration_seconds']:.1f} seconds")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Scraping interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        print(f"\n🏁 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    # Add scrapers here
    # Example: scraper_manager.add_scraper(EbayScraper())
    
    # Run the scraper
    exit_code = main()
    sys.exit(exit_code) 