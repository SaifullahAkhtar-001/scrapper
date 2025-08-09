from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup
import sys
import os
import time
import re
from datetime import datetime

# Add the parent directory to the Python path so we can import from scrapers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import scraper_manager
from scrapers.todocoleccion_scraper import TodocoleccionScraper

class TodocoleccionService:

    @staticmethod
    def run_complete_scraping() -> Dict[str, Any]:
        """
        Run complete scraping for all keywords with full pagination support.
        This is the main production function that scrapes all keywords systematically.
        """
        start_time = datetime.now()
        print(f"Starting complete Todocoleccion scraping at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Get all keywords from database
            keywords = scraper_manager.get_spanish_keywords()
            
            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database. Please add some keywords first.',
                    'total_runtime': 0
                }

            # Get the Todocoleccion scraper
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not found in scraper manager',
                    'total_runtime': 0
                }

            print(f"Found {len(keywords)} keywords to process")
            print(f"Keywords: {', '.join(keywords)}")
            print("-" * 80)
            
            # Initialize URL cache for optimal performance
            print("Initializing URL cache for duplicate checking...")
            todocoleccion_scraper.initialize_url_cache()

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

            # Process each keyword
            for i, keyword in enumerate(keywords, 1):
                keyword_start_time = datetime.now()
                print(f"\n[{i}/{len(keywords)}] Processing keyword: '{keyword}'")
                print("-" * 40)
                
                try:
                    # Run scraper for this keyword with full pagination
                    result = TodocoleccionService.scrape_keyword_with_pagination(
                        todocoleccion_scraper, 
                        keyword
                    )
                    
                    # Update totals
                    total_results['keywords_processed'] += 1
                    
                    if result['success']:
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
                        'success': result['success'],
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
                    if result['success']:
                        print(f"✅ '{keyword}' completed successfully!")
                        print(f"   📊 Found: {result['total_listings_found']} listings")
                        print(f"   💾 Saved: {result['saved_listings']} listings")
                        print(f"   📄 Pages: {result['pages_scraped']} pages")
                        print(f"   ⏱️  Time: {runtime:.1f} seconds")
                        if result['errors'] > 0:
                            print(f"   ⚠️  Errors: {result['errors']}")
                    else:
                        print(f"❌ '{keyword}' failed: {result.get('error', 'Unknown error')}")
                        print(f"   ⏱️  Time: {runtime:.1f} seconds")
                    
                    # Add delay between keywords to be respectful to the server
                    if i < len(keywords):  # Don't wait after the last keyword
                        print(f"   ⏸️  Waiting 3 seconds before next keyword...")
                        time.sleep(3)
                        
                except Exception as e:
                    total_results['keywords_processed'] += 1
                    total_results['keywords_failed'] += 1
                    
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
            print("COMPLETE SCRAPING SUMMARY")
            print("=" * 80)
            print(f"🕒 Total Runtime: {total_runtime:.1f} seconds ({total_runtime/60:.1f} minutes)")
            print(f"📝 Keywords Processed: {total_results['keywords_processed']}")
            print(f"✅ Keywords Successful: {total_results['keywords_successful']}")
            print(f"❌ Keywords Failed: {total_results['keywords_failed']}")
            print(f"📊 Total Listings Found: {total_results['total_listings_found']}")
            print(f"💾 Total Listings Saved: {total_results['total_listings_saved']}")
            print(f"📄 Total Pages Scraped: {total_results['total_pages_scraped']}")
            print(f"⚠️  Total Errors: {total_results['total_errors']}")
            
            if total_results['total_listings_found'] > 0:
                success_rate = (total_results['total_listings_saved'] / total_results['total_listings_found']) * 100
                print(f"📈 Success Rate: {success_rate:.1f}%")
            
            print("\n📋 Individual Keyword Results:")
            for result in total_results['keyword_results']:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {result['keyword']}: {result['listings_saved']} saved / {result['listings_found']} found ({result['pages_scraped']} pages, {result['runtime']:.1f}s)")
                if not result['success'] and result['error_message']:
                    print(f"      Error: {result['error_message']}")

            return {
                'success': True,
                'message': 'Complete scraping finished',
                'total_runtime': total_runtime,
                'summary': total_results
            }

        except Exception as e:
            total_runtime = (datetime.now() - start_time).total_seconds()
            print(f"\n❌ Fatal error during complete scraping: {str(e)}")
            
            return {
                'success': False,
                'error': f'Fatal error during scraping: {str(e)}',
                'total_runtime': total_runtime
            }

    @staticmethod
    def scrape_keyword_with_pagination(scraper: TodocoleccionScraper, keyword: str) -> Dict[str, Any]:
        """
        Scrape a single keyword with full pagination support.
        Continues scraping until no more results or rate limited.
        """
        try:
            print(f"🔍 Starting pagination scraping for '{keyword}'")
            
            # Initialize tracking
            page = 1
            total_listings = 0
            saved_listings = 0
            total_errors = 0
            consecutive_empty_pages = 0
            max_consecutive_empty_pages = 3  # Stop after 3 consecutive empty pages
            
            while True:
                try:
                    print(f"  📄 Scraping page {page}...")
                    
                    # Build search URL for current page
                    search_url = scraper.build_search_url(keyword, page)
                    print(f"  🔍 Search URL: {search_url}")
                    # Fetch page content with better headers
                    headers = {
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                         'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                         'Accept-Encoding': 'gzip, deflate, br',
                         'DNT': '1',
                         'Connection': 'keep-alive',
                         'Upgrade-Insecure-Requests': '1',
                         'Sec-Fetch-Dest': 'document',
                         'Sec-Fetch-Mode': 'navigate',
                         'Sec-Fetch-Site': 'none',
                         'Sec-Fetch-User': '?1',
                         'Cache-Control': 'max-age=0'
                     }
                     
                     # Add delay before request
                    time.sleep(2)
                     
                    response = requests.get(search_url, headers=headers, timeout=15)
                    print(f"  🔍 Response status: {response}")
                    if response.status_code == 403:
                        print(f"  🚫 Rate limited (403) on page {page}. Stopping pagination.")
                        break
                    elif response.status_code == 404:
                        print(f"  🏁 Reached end of pagination (404) on page {page}. Moving to next keyword.")
                        break
                    elif response.status_code != 200:
                        print(f"  ⚠️  HTTP {response.status_code} on page {page}. Skipping...")
                        total_errors += 1
                        page += 1
                        time.sleep(2)
                        continue
                    
                    # Extract listings from page
                    page_listings = scraper.extract_listings_from_page(response.text, keyword)
                    
                    if not page_listings:
                        consecutive_empty_pages += 1
                        print(f"  📭 No listings found on page {page} (empty page {consecutive_empty_pages}/{max_consecutive_empty_pages})")
                        
                        if consecutive_empty_pages >= max_consecutive_empty_pages:
                            print(f"  🏁 Reached {max_consecutive_empty_pages} consecutive empty pages. Ending pagination.")
                            break
                    else:
                        consecutive_empty_pages = 0  # Reset counter
                        print(f"  ✅ Found {len(page_listings)} listings on page {page}")
                        
                        # Process and save listings
                        page_saved = 0
                        for listing in page_listings:
                            try:
                                # Save listing to database using the scraper's save_listing method
                                if scraper.save_listing(listing):
                                    page_saved += 1
                            except Exception as save_error:
                                total_errors += 1
                                print(f"    ⚠️  Error saving listing: {save_error}")
                        
                        total_listings += len(page_listings)
                        saved_listings += page_saved
                        print(f"  💾 Saved {page_saved}/{len(page_listings)} listings from page {page}")
                    
                    # Move to next page
                    page += 1
                    
                    # Add delay between pages to be respectful
                    time.sleep(1.5)
                    
                    # Safety check to prevent infinite loops
                    if page > 1000:  # Reasonable upper limit
                        print(f"  🛑 Reached page limit (1000). Stopping pagination.")
                        break
                        
                except requests.exceptions.RequestException as req_error:
                    print(f"  🌐 Request error on page {page}: {req_error}")
                    total_errors += 1
                    
                    # Try to continue with next page after a longer delay
                    time.sleep(5)
                    page += 1
                    continue
                    
                except Exception as page_error:
                    print(f"  ❌ Error processing page {page}: {page_error}")
                    total_errors += 1
                    page += 1
                    continue
            
            print(f"🏁 Pagination complete for '{keyword}': {total_listings} found, {saved_listings} saved across {page-1} pages")
            
            return {
                'success': True,
                'keyword': keyword,
                'site': 'todocoleccion',
                'total_listings_found': total_listings,
                'saved_listings': saved_listings,
                'pages_scraped': page - 1,
                'errors': total_errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'keyword': keyword,
                'error': str(e),
                'total_listings_found': 0,
                'saved_listings': 0,
                'pages_scraped': 0,
                'errors': 1
            }

    @staticmethod
    def scrape_specific_keyword(keyword: str) -> Dict[str, Any]:
        """
        Scrape Todocoleccion for a single keyword using full pagination.
        """
        try:
            # Locate the Todocoleccion scraper instance
            todocoleccion_scraper = None
            for scraper in scraper_manager.scrapers:
                if scraper.site_name == 'todocoleccion':
                    todocoleccion_scraper = scraper
                    break

            if not todocoleccion_scraper:
                return {
                    'success': False,
                    'error': 'Todocoleccion scraper not found in scraper manager'
                }

            # Run pagination scraping for the provided keyword
            result = TodocoleccionService.scrape_keyword_with_pagination(
                todocoleccion_scraper, keyword
            )
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_keyword_page_count(keyword: str) -> int:
        """
        Get the estimated number of pages for a keyword by checking the first page.
        This helps estimate the scope of scraping.
        """
        try:
            scraper = TodocoleccionScraper()
            search_url = scraper.build_search_url(keyword, 1)
            
            response = requests.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                # Try to extract pagination info from the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for pagination elements that might indicate total pages
                # This is site-specific and might need adjustment
                pagination_elements = soup.find_all(['a', 'span'], class_=lambda x: x and 'pag' in str(x).lower())
                
                max_page = 1
                for elem in pagination_elements:
                    text = elem.get_text(strip=True)
                    if text.isdigit():
                        page_num = int(text)
                        if page_num > max_page:
                            max_page = page_num
                
                return max_page
            else:
                return 1
                
        except Exception:
            return 1  # Default to 1 if we can't determine

    @staticmethod
    def preview_scraping_scope() -> Dict[str, Any]:
        """
        Preview the scope of scraping without actually doing it.
        Shows estimated pages and listings for each keyword.
        """
        try:
            keywords = scraper_manager.get_keywords()
            
            if not keywords:
                return {
                    'success': False,
                    'error': 'No keywords found in database.'
                }
            
            print("🔍 SCRAPING SCOPE PREVIEW")
            print("=" * 60)
            
            preview_data = []
            total_estimated_pages = 0
            
            for keyword in keywords:
                print(f"Checking '{keyword}'...")
                estimated_pages = TodocoleccionService.get_keyword_page_count(keyword)
                estimated_listings = estimated_pages * 30  # Rough estimate of listings per page
                
                preview_data.append({
                    'keyword': keyword,
                    'estimated_pages': estimated_pages,
                    'estimated_listings': estimated_listings
                })
                
                total_estimated_pages += estimated_pages
                print(f"  📄 Estimated pages: {estimated_pages}")
                print(f"  📊 Estimated listings: {estimated_listings}")
                
                time.sleep(1)  # Small delay between requests
            
            print("\n" + "=" * 60)
            print("PREVIEW SUMMARY")
            print("=" * 60)
            print(f"Total keywords: {len(keywords)}")
            print(f"Total estimated pages: {total_estimated_pages}")
            print(f"Total estimated listings: {sum(item['estimated_listings'] for item in preview_data)}")
            print(f"Estimated time: {total_estimated_pages * 2 / 60:.1f} minutes (rough estimate)")
            
            return {
                'success': True,
                'keywords_count': len(keywords),
                'total_estimated_pages': total_estimated_pages,
                'preview_data': preview_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def push_cigar_listings_from_scraped():
        """
        Filter listings from 'scraped_listings' by keywords and stopwords in Python, and sync 'cigar_listings' to match the filter.
        - Remove any listing from cigar_listings that does not match the filter.
        - Insert new filtered listings not already present.
        - Fetch keywords and stopwords from the DB (both English and Spanish fields, active only).
        """
        from config.supabase_client import supabase_client
        from services.keyword_service import KeywordService
        from services.stopword_service import StopwordService

        # Fetch active keywords (both English and Spanish)
        try:
            db_keywords = KeywordService.get_all_keywords()
            keywords = set()
            for k in db_keywords:
                if k.get('keyword'):
                    keywords.add(k['keyword'].strip().upper())
                if k.get('spanishkeyword'):
                    keywords.add(k['spanishkeyword'].strip().upper())
            keywords = [kw for kw in keywords if kw]
        except Exception as e:
            print(f"Error fetching keywords: {e}")
            return {'success': False, 'error': f'Error fetching keywords: {e}'}

        # Fetch active stopwords (both English and Spanish)
        try:
            db_stopwords = StopwordService.get_all_stopwords()
            stop_words = set()
            for sw in db_stopwords:
                if sw.get('stopword'):
                    stop_words.add(sw['stopword'].strip().upper())
                if sw.get('spanishkeyword'):
                    stop_words.add(sw['spanishkeyword'].strip().upper())
            stop_words = [sw for sw in stop_words if sw]
        except Exception as e:
            print(f"Error fetching stopwords: {e}")
            return {'success': False, 'error': f'Error fetching stopwords: {e}'}

        # Fetch all listings from scraped_listings
        try:
            response = supabase_client.client.table('scraped_listings').select('*').execute()
            listings = response.data
        except Exception as e:
            print(f"Error fetching scraped_listings: {e}")
            return {'success': False, 'error': str(e)}

        if not listings:
            print("No listings found in scraped_listings.")
            return {'success': False, 'error': 'No listings found in scraped_listings.'}

        filtered = []
        filtered_urls = set()
        for listing in listings:
            title = (listing.get('title') or '').upper()
            url = (listing.get('url') or '').upper()
            # Must match at least one keyword in title or url
            if not any(kw in title or kw in url for kw in keywords):
                continue
            # Exclude if any stopword is present in title or url
            if any(sw in title or sw in url for sw in stop_words):
                continue
            filtered.append(listing)
            if 'url' in listing:
                filtered_urls.add(listing['url'])

        print(f"Filtered {len(filtered)} listings to sync with cigar_listings.")
        if not filtered:
            # If nothing matches, clear the cigar_listings table
            try:
                del_resp = supabase_client.client.table('cigar_listings').delete().neq('id', 0).execute()
                print(f"Deleted all listings from cigar_listings (no matches after filtering).")
            except Exception as e:
                print(f"Error clearing cigar_listings: {e}")
            return {'success': True, 'message': 'No listings matched filter. cigar_listings cleared.'}

        # Fetch all URLs from cigar_listings
        try:
            cigar_resp = supabase_client.client.table('cigar_listings').select('id,url').execute()
            cigar_data = cigar_resp.data
            existing_urls = set(item['url'] for item in cigar_data if 'url' in item)
            id_url_map = {item['url']: item['id'] for item in cigar_data if 'url' in item and 'id' in item}
        except Exception as e:
            print(f"Error fetching cigar_listings URLs: {e}")
            return {'success': False, 'error': str(e)}

        # Delete from cigar_listings any listing whose URL is not in filtered_urls
        urls_to_remove = existing_urls - filtered_urls
        deleted_count = 0
        if urls_to_remove:
            try:
                for url in urls_to_remove:
                    # Delete by id for safety
                    del_id = id_url_map.get(url)
                    if del_id:
                        supabase_client.client.table('cigar_listings').delete().eq('id', del_id).execute()
                        deleted_count += 1
                print(f"Deleted {deleted_count} listings from cigar_listings (no longer matching filter).")
            except Exception as e:
                print(f"Error deleting from cigar_listings: {e}")
                return {'success': False, 'error': str(e)}

        # Only keep listings whose URL is not already in cigar_listings
        to_insert = [l for l in filtered if l.get('url') not in existing_urls]

        print(f"{len(to_insert)} new listings to insert into cigar_listings (after duplicate check).")
        if to_insert:
            try:
                # Remove 'id' if present, let DB assign new id
                for l in to_insert:
                    l.pop('id', None)
                insert_resp = supabase_client.client.table('cigar_listings').upsert(to_insert).execute()
                print(f"Inserted {len(insert_resp.data)} listings into cigar_listings.")
            except Exception as e:
                print(f"Error inserting into cigar_listings: {e}")
                return {'success': False, 'error': str(e)}

        return {
            'success': True,
            'inserted': len(to_insert),
            'deleted': deleted_count,
            'message': f'Synced cigar_listings to match current filter.'
        }

    # Keep existing test functions for debugging...
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
    def quick_test():
        """Quick test for immediate debugging"""
        print("\n=== Quick Todocoleccion Test ===")
        
        try:
            scraper = TodocoleccionScraper()
            test_keyword = "cigarro"  # Simpler keyword for testing
            
            print(f"Testing with keyword: '{test_keyword}'")
            
            # Test URL building
            url = scraper.build_search_url(test_keyword, 1)
            print(f"Search URL: {url}")
            
            # Quick fetch test with improved headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            print("Testing with improved headers...")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.find_all('div', class_='card-lote card-lote-as-gallery')
                print(f"Found {len(items)} items on first page")
                
                if items:
                    print("✅ Basic scraping is working!")
                else:
                    print("⚠️  No items found - check selectors")
            elif response.status_code == 403:
                print("❌ Still getting 403 - website is blocking requests")
                print("Trying with different approach...")
                
                # Try with session approach
                session = requests.Session()
                session.headers.update(headers)
                response2 = session.get(url, timeout=10)
                print(f"Session response status: {response2.status_code}")
                
            else:
                print(f"❌ Failed to fetch page: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Quick test failed: {e}")

# Usage examples:
if __name__ == "__main__":
    # Preview the scope before running
    # TodocoleccionService.preview_scraping_scope()
    
    # Run the complete scraping
    result = TodocoleccionService.run_complete_scraping()
    print(f"\nFinal result: {result['success']}")
    
    # Or run a quick test for debugging
    # TodocoleccionService.quick_test()