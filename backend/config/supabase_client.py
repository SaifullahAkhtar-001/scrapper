import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(self.url, self.key)
    
    def get_all_keywords(self):
        """Fetch all active keywords from the database"""
        try:
            response = self.client.table('keywords').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching keywords: {e}")
            return []
    def get_all_spanish_keywords(self):
        """Fetch all active keywords from the database"""
        try:
            response = self.client.table('keywords').select('spanishkeyword').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching keywords: {e}")
            return []
    
    def save_listing(self, listing_data):
        """Save a scraped listing to the database"""
        try:
            response = self.client.table('scraped_listings').upsert(listing_data).execute()
            return response.data
        except Exception as e:
            print(f"Error saving listing: {e}")
            return None
    
    def check_url_exists(self, url):
        """Check if a URL already exists in the database"""
        try:
            response = self.client.table('scraped_listings').select('id').eq('url', url).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking URL: {e}")
            return False

    def get_app_setting(self, key: str, default=None):
        """Fetch a single app_settings value by key."""
        try:
            response = (
                self.client.table('app_settings')
                .select('value')
                .eq('key', key)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0]['value']
            return default
        except Exception as e:
            print(f"Error fetching app setting '{key}': {e}")
            return default

# Create a global instance
supabase_client = SupabaseClient() 