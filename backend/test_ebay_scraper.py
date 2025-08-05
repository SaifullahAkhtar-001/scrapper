#!/usr/bin/env python3
"""
Test script for eBay scraper
Run this to test the eBay scraper functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.ebay_scraper import EbayScraper
from config.supabase_client import supabase_client

def test_ebay_scraper():
    """Test the eBay scraper with a sample keyword"""
    
    print("=== Testing eBay Scraper ===")
    
    # Test database connection
    try:
        keywords = supabase_client.get_all_keywords()
        print(f"✓ Database connection successful. Found {len(keywords)} keywords")
        
        if not keywords:
            print("⚠ No keywords found in database. Using test keyword.")
            test_keywords = ["vintage cigars"]
        else:
            test_keywords = [kw['keyword'] for kw in keywords[:1]]  # Use first keyword
            print(f"✓ Using keyword: {test_keywords[0]}")
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("⚠ Using test keyword without database.")
        test_keywords = ["vintage cigars"]
    
    # Create eBay scraper
    try:
        scraper = EbayScraper()
        print("✓ eBay scraper created successfully")
    except Exception as e:
        print(f"✗ Failed to create eBay scraper: {e}")
        return
    
    # Test URL building
    try:
        test_url = scraper.build_search_url(test_keywords[0])
        print(f"✓ Search URL built: {test_url}")
    except Exception as e:
        print(f"✗ Failed to build search URL: {e}")
        return
    
    # Test single keyword scraping
    try:
        print(f"\n--- Starting scraping for '{test_keywords[0]}' ---")
        result = scraper.scrape_keyword(test_keywords[0], max_pages=1)  # Only scrape 1 page for testing
        
        print(f"\n=== Scraping Results ===")
        print(f"Keyword: {result['keyword']}")
        print(f"Site: {result['site']}")
        print(f"Total listings found: {result['total_listings_found']}")
        print(f"Saved listings: {result['saved_listings']}")
        print(f"Errors: {result['errors']}")
        print(f"Pages scraped: {result['pages_scraped']}")
        
        if result['total_listings_found'] > 0:
            print("✓ Scraping successful!")
        else:
            print("⚠ No listings found. This might be normal for some keywords.")
            
    except Exception as e:
        print(f"✗ Scraping failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ebay_scraper() 