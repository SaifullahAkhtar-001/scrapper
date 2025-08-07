from scrapers.craigslist_scraper import CraigslistScraper

if __name__ == "__main__":
    scraper = CraigslistScraper()
    test_keyword = "cigars"
    print(f"Testing CraigslistScraper with keyword: {test_keyword}")
    result = scraper.scrape_keyword(test_keyword, max_pages=2)
    print("Result:")
    print(result)