import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class CraigslistScraper(BaseScraper):
    """
    Scraper for https://searchcraigslist.net
    Handles pagination and extracts listings from search results
    """
    def __init__(self):
        super().__init__("craigslist")
        self.base_url = "https://searchcraigslist.net/results"

    def build_search_url(self, keyword: str, page: int = 1) -> str:
        # The search URL uses 'q' for keyword and gsc.page for pagination
        # Example: https://searchcraigslist.net/results?q=cigars#gsc.tab=0&gsc.q=cigars&gsc.page=1
        clean_keyword = keyword.replace(' ', '+')
        return f"{self.base_url}?q={clean_keyword}#gsc.tab=0&gsc.q={clean_keyword}&gsc.page={page}"

    def extract_listings_from_page(self, html_content: str, keyword: str) -> List[Dict[str, Any]]:
        listings = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Each result is in a div with class 'gsc-webResult gsc-result'
            result_divs = soup.find_all('div', class_='gsc-webResult gsc-result')
            for div in result_divs:
                try:
                    # Title and URL
                    title_a = div.find('a', class_='gs-title')
                    if not title_a or not title_a.text.strip():
                        continue
                    title = title_a.get_text(strip=True)
                    url = title_a.get('href')
                    if not url:
                        continue
                    # Image (optional)
                    img_tag = div.find('img', class_='gs-image')
                    image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
                    # Snippet/description
                    snippet_div = div.find('div', class_='gs-snippet')
                    description = snippet_div.get_text(strip=True) if snippet_div else ''
                    # Compose listing
                    listing = {
                        'title': self.clean_title(title),
                        'price': None,  # Craigslist search aggregator does not show price in results
                        'url': url,
                        'image_url': image_url,
                        'description': description,
                        'site': self.site_name,
                        'keyword': keyword,
                    }
                    listings.append(listing)
                except Exception as e:
                    print(f"Error extracting a listing: {e}")
                    continue
        except Exception as e:
            print(f"Error parsing Craigslist HTML: {e}")
        return listings