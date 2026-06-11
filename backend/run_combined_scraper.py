#!/usr/bin/env python3
"""
Combined Scraper Runner Script

This script provides an easy way to run both Craigslist and TodoColeccion scrapers
with different options and configurations.

Usage:
    python run_combined_scraper.py                    # Run full scraping (if enabled in app_settings)
    python run_combined_scraper.py --quick           # Run quick test
    python run_combined_scraper.py --force           # Run even when is_scraper_running is false
    python run_combined_scraper.py --help            # Show help
"""

import sys
import os
import argparse
from datetime import datetime

# Add the services directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.supabase_client import supabase_client


def is_scraper_enabled() -> bool:
    """Return True only when is_scraper_running is explicitly true in app_settings."""
    value = supabase_client.get_app_setting('is_scraper_running', default=False)
    return value is True


def main():
    parser = argparse.ArgumentParser(
        description='Run combined Craigslist and TodoColeccion scrapers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_combined_scraper.py                    # Run full scraping
  python run_combined_scraper.py --quick           # Run quick test
  python run_combined_scraper.py --verbose         # Run with verbose output
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run a quick test with limited scope'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='combined_scraper.log',
        help='Log file name (default: combined_scraper.log)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Run even if is_scraper_running is false in app_settings'
    )
    
    args = parser.parse_args()

    if not args.force and not is_scraper_enabled():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Scraper disabled (is_scraper_running=false). Skipping.")
        sys.exit(0)
    
    # Print header
    print("=" * 80)
    print("🚀 COMBINED SCRAPER RUNNER")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Quick Test' if args.quick else 'Full Scraping'}")
    print(f"Log file: {args.log_file}")
    print("=" * 80)
    
    try:
        # Import the combined service
        from services.combined_scraper_service import CombinedScraperService
        
        # Run the appropriate scraping mode
        if args.quick:
            print("\n🧪 Running quick test mode...")
            result = CombinedScraperService.run_quick_test()
        else:
            print("\n🚀 Running full scraping mode...")
            result = CombinedScraperService.run_complete_scraping()
        
        # Print final results
        print("\n" + "=" * 80)
        print("🎯 FINAL RESULTS")
        print("=" * 80)
        print(f"Overall Success: {'✅' if result['success'] else '❌'}")
        print(f"Total Runtime: {result.get('total_runtime', 0):.1f} seconds")
        
        if not result['success']:
            print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            # Print detailed results if available
            if 'combined_results' in result:
                combined = result['combined_results']
                print(f"\nScrapers Run: {len(combined['scrapers_run'])}/{len(combined['scraper_results'])}")
                print(f"Total Listings Found: {combined['total_listings_found']}")
                print(f"Total Listings Saved: {combined['total_listings_saved']}")
                print(f"Total Errors: {combined['total_errors']}")
                
                # Print individual scraper results
                print("\n📊 Individual Scraper Results:")
                for scraper_name, scraper_data in combined['scraper_results'].items():
                    status = "✅" if scraper_data['success'] else "❌"
                    print(f"  {status} {scraper_name.upper()}: {scraper_data['runtime']:.1f}s")
                    if not scraper_data['success']:
                        print(f"      Error: {scraper_data['result'].get('error', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print("🏁 Combined scraper execution completed!")
        print("=" * 80)
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
