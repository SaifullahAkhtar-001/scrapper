#!/usr/bin/env python3
"""
Test script for database integration
This script tests the database connection and ensures the scraper can save data correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.supabase_client import supabase_client
from scrapers.todocoleccion_scraper import TodocoleccionScraper

def test_database_connection():
    """Test database connection and keywords retrieval"""
    print("=== Testing Database Connection ===")
    
    try:
        # Test keywords retrieval
        keywords = supabase_client.get_all_keywords()
        print(f"✅ Successfully retrieved {len(keywords)} keywords from database")
        
        if keywords:
            print("Sample keywords:")
            for i, kw in enumerate(keywords[:5]):
                print(f"  {i+1}. {kw['keyword']}")
        else:
            print("⚠️  No keywords found in database")
            
        return keywords
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return []

def test_listing_save():
    """Test saving a sample listing to database"""
    print("\n=== Testing Listing Save ===")
    
    # Create a sample listing that matches the database schema
    sample_listing = {
        'title': 'Test Vintage Cigar Cutter',
        'url': 'https://www.todocoleccion.net/test-item-123',
        'price': 45.99,
        'image_url': 'https://example.com/test-image.jpg',
        'description': 'This is a test description for a vintage cigar cutter',
        'site': 'todocoleccion',
        'keyword': 'cigarro antiguo'
    }
    
    try:
        # Check if URL exists
        exists = supabase_client.check_url_exists(sample_listing['url'])
        if exists:
            print(f"⚠️  Test URL already exists in database")
            return True
        
        # Save the listing
        result = supabase_client.save_listing(sample_listing)
        if result:
            print(f"✅ Successfully saved test listing to database")
            return True
        else:
            print(f"❌ Failed to save test listing")
            return False
            
    except Exception as e:
        print(f"❌ Error saving test listing: {e}")
        return False

def test_scraper_integration():
    """Test scraper with database integration"""
    print("\n=== Testing Scraper Integration ===")
    
    try:
        # Create scraper instance
        scraper = TodocoleccionScraper()
        print(f"✅ Scraper initialized: {scraper.site_name}")
        
        # Test with a simple keyword
        test_keyword = "cigarro"
        print(f"Testing with keyword: '{test_keyword}'")
        
        # Run scraper for just 1 page to test
        result = scraper.scrape_keyword(test_keyword, max_pages=1)
        
        print(f"✅ Scraper test completed:")
        print(f"  - Total listings found: {result['total_listings_found']}")
        print(f"  - Saved listings: {result['saved_listings']}")
        print(f"  - Errors: {result['errors']}")
        print(f"  - Pages scraped: {result['pages_scraped']}")
        
        return result['saved_listings'] > 0
        
    except Exception as e:
        print(f"❌ Scraper integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Database Integration Test")
    print("=" * 50)
    
    # Test 1: Database connection
    keywords = test_database_connection()
    
    # Test 2: Listing save
    save_success = test_listing_save()
    
    # Test 3: Scraper integration (only if we have keywords)
    scraper_success = False
    if keywords:
        scraper_success = test_scraper_integration()
    else:
        print("\n⚠️  Skipping scraper test - no keywords in database")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Database connection: {'✅ PASS' if keywords is not None else '❌ FAIL'}")
    print(f"Listing save: {'✅ PASS' if save_success else '❌ FAIL'}")
    print(f"Scraper integration: {'✅ PASS' if scraper_success else '❌ FAIL'}")
    
    if keywords is not None and save_success:
        print("\n🎉 Database integration is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Please check the database configuration.")

if __name__ == "__main__":
    main() 