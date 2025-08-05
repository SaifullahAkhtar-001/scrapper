#!/usr/bin/env python3
"""
Enhanced test script for Todocoleccion scraper
This script tests the scraper with detailed debugging to ensure it extracts all data correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.todocoleccion_scraper import TodocoleccionScraper
import requests
from bs4 import BeautifulSoup

def test_html_parsing():
    """Test HTML parsing with actual page content"""
    print("=== Testing HTML Parsing ===")
    
    scraper = TodocoleccionScraper()
    test_keyword = "cigarro antiguo"
    
    # Get actual page content
    search_url = scraper.build_search_url(test_keyword, 1)
    print(f"Fetching: {search_url}")
    
    try:
        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if response.status_code == 200:
            print(f"Successfully fetched page (status: {response.status_code})")
            
            # Parse with BeautifulSoup to test structure
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for main container
            main_container = soup.find('div', id='buscador-lote-items-container')
            if main_container:
                print("✅ Found main search container")
            else:
                print("❌ Main search container not found")
                
            # Check for items container
            items_container = soup.find('div', class_=lambda x: x and '_lote_items' in x)
            if items_container:
                print("✅ Found items container")
                print(f"Items container classes: {items_container.get('class')}")
            else:
                print("❌ Items container not found")
            
            # Check for individual items
            listing_elements = soup.find_all('div', class_='_lote_item')
            print(f"✅ Found {len(listing_elements)} listing elements")
            
            if listing_elements:
                # Test parsing first few items
                print("\n--- Testing first 3 listings ---")
                for i, element in enumerate(listing_elements[:3]):
                    print(f"\nListing {i+1}:")
                    lote_id = element.get('data-id-lote', 'unknown')
                    print(f"  Lote ID: {lote_id}")
                    
                    # Test title extraction
                    title_elem = element.select_one('h2._lote_item-titulo a')
                    if title_elem:
                        title = title_elem.get('title') or title_elem.get_text(strip=True)
                        print(f"  Title: {title[:60]}{'...' if len(title) > 60 else ''}")
                    else:
                        print("  Title: NOT FOUND")
                    
                    # Test price extraction
                    price_elem = element.select_one('span.precio-lote-listado._lote_item-precio')
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        print(f"  Price: {price}")
                    else:
                        print("  Price: NOT FOUND")
                    
                    # Test URL extraction
                    url_elem = element.select_one('h2._lote_item-titulo a')
                    if url_elem:
                        url = url_elem.get('href')
                        print(f"  URL: {url[:60]}{'...' if len(url) > 60 else ''}")
                    else:
                        print("  URL: NOT FOUND")
                    
                    # Test image extraction
                    img_elem = element.select_one('a._lote_item-img-main-link')
                    if img_elem:
                        img_url = img_elem.get('data-image-url')
                        print(f"  Image: {img_url[:60] if img_url else 'NO DATA-IMAGE-URL'}{'...' if img_url and len(img_url) > 60 else ''}")
                    else:
                        print("  Image: NOT FOUND")
            
            # Now test the scraper's extraction method
            print(f"\n--- Testing scraper extraction ---")
            listings = scraper.extract_listings_from_page(response.text, test_keyword)
            print(f"Scraper extracted {len(listings)} listings")
            
            if listings:
                print(f"\nFirst extracted listing:")
                first_listing = listings[0]
                for key, value in first_listing.items():
                    if isinstance(value, str) and len(str(value)) > 60:
                        print(f"  {key}: {str(value)[:60]}...")
                    else:
                        print(f"  {key}: {value}")
            
        else:
            print(f"Failed to fetch page (status: {response.status_code})")
            
    except Exception as e:
        print(f"Error testing HTML parsing: {e}")
        import traceback
        traceback.print_exc()

def test_todocoleccion_scraper():
    """Test the complete scraper functionality"""
    
    print("\n=== Testing Complete Scraper ===")
    
    # Create scraper instance
    scraper = TodocoleccionScraper()
    
    print(f"Scraper initialized: {scraper.site_name}")
    print(f"Base URL: {scraper.base_url}")
    
    # Test with the cigarro antiguo keyword that should have 8320 entries
    test_keyword = "cigarro antiguo"
    
    print(f"\n--- Testing with keyword: '{test_keyword}' ---")
    print("This should find many listings (you mentioned 8320 entries)")
    
    try:
        # Run scraper for first 3 pages to test thoroughly
        result = scraper.scrape_keyword(test_keyword)
        
        print(f"\n=== Scraping Results ===")
        print(f"Keyword: {result['keyword']}")
        print(f"Site: {result['site']}")
        print(f"Total listings found: {result['total_listings_found']}")
        print(f"Saved listings: {result['saved_listings']}")
        print(f"Errors: {result['errors']}")
        print(f"Pages scraped: {result['pages_scraped']}")
        
        # Calculate success rate
        if result['total_listings_found'] > 0:
            success_rate = (result['saved_listings'] / result['total_listings_found']) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        if result['total_listings_found'] > 30:  # Should find many listings per page
            print(f"\n✅ Scraper is working correctly!")
            print(f"Found {result['total_listings_found']} listings across {result['pages_scraped']} pages")
        elif result['total_listings_found'] > 0:
            print(f"\n⚠️  Scraper found some listings but fewer than expected")
            print(f"This might indicate the extraction logic needs refinement")
        else:
            print(f"\n❌ No listings found - there's likely an issue with the extraction logic")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

def test_url_building():
    """Test URL building for different scenarios"""
    print("\n=== Testing URL Building ===")
    
    scraper = TodocoleccionScraper()
    
    test_cases = [
        ("cigarro antiguo", 1),
        ("cigarro antiguo", 2),
        ("vintage cigarette", 1),
        ("antique tobacco", 10),
    ]
    
    for keyword, page in test_cases:
        url = scraper.build_search_url(keyword, page)
        print(f"'{keyword}' page {page} -> {url}")

def main():
    print("Todocoleccion Scraper Enhanced Test")
    print("=" * 60)
    
    # Test URL building
    test_url_building()
    
    # Test HTML parsing with actual content
    test_html_parsing()
    
    # Test complete scraper
    test_todocoleccion_scraper()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("\nIf you see issues with extraction, check:")
    print("1. The DOM structure hasn't changed")
    print("2. The CSS selectors are correct")
    print("3. The website isn't blocking the requests")
    print("4. The pagination logic is working")

if __name__ == "__main__":
    main()