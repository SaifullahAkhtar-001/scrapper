from typing import List, Dict, Any, Optional
from config.supabase_client import supabase_client

class KeywordService:
    """Service class for keyword CRUD operations"""
    
    @staticmethod
    def get_all_keywords() -> List[Dict[str, Any]]:
        """Get all active keywords"""
        try:
            response = supabase_client.client.table('keywords').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error fetching keywords: {e}")
    
    @staticmethod
    def get_keyword_by_id(keyword_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific keyword by ID"""
        try:
            response = supabase_client.client.table('keywords').select('*').eq('id', keyword_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching keyword: {e}")
    
    @staticmethod
    def add_keywords(keywords: List[str]) -> Dict[str, Any]:
        """Add multiple keywords"""
        try:
            # Prepare data for insertion
            keyword_data = []
            for keyword in keywords:
                if keyword.strip():  # Skip empty keywords
                    keyword_data.append({
                        'keyword': keyword.strip(),
                        'is_active': True
                    })
            
            if not keyword_data:
                raise Exception("No valid keywords provided")
            
            # Insert keywords using upsert to avoid duplicates
            response = supabase_client.client.table('keywords').upsert(keyword_data).execute()
            
            return {
                'success': True,
                'message': f'Successfully added {len(response.data)} keywords',
                'keywords_added': len(response.data),
                'data': response.data
            }
        except Exception as e:
            raise Exception(f"Error adding keywords: {e}")
    
    @staticmethod
    def update_keyword(keyword_id: int, keyword: str, is_active: bool = True) -> Dict[str, Any]:
        """Update a specific keyword"""
        try:
            # Check if keyword exists
            existing = KeywordService.get_keyword_by_id(keyword_id)
            if not existing:
                raise Exception(f"Keyword with ID {keyword_id} not found")
            
            # Update the keyword
            response = supabase_client.client.table('keywords').update({
                'keyword': keyword.strip(),
                'is_active': is_active
            }).eq('id', keyword_id).execute()
            
            return {
                'success': True,
                'message': f'Successfully updated keyword ID {keyword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error updating keyword: {e}")
    
    @staticmethod
    def delete_keyword(keyword_id: int) -> Dict[str, Any]:
        """Delete a keyword (soft delete by setting is_active to False)"""
        try:
            # Check if keyword exists
            existing = KeywordService.get_keyword_by_id(keyword_id)
            if not existing:
                raise Exception(f"Keyword with ID {keyword_id} not found")
            
            # Soft delete by setting is_active to False
            response = supabase_client.client.table('keywords').update({
                'is_active': False
            }).eq('id', keyword_id).execute()
            
            return {
                'success': True,
                'message': f'Successfully deleted keyword ID {keyword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error deleting keyword: {e}")
    
    @staticmethod
    def hard_delete_keyword(keyword_id: int) -> Dict[str, Any]:
        """Permanently delete a keyword from database"""
        try:
            # Check if keyword exists
            existing = KeywordService.get_keyword_by_id(keyword_id)
            if not existing:
                raise Exception(f"Keyword with ID {keyword_id} not found")
            
            # Permanently delete
            response = supabase_client.client.table('keywords').delete().eq('id', keyword_id).execute()
            
            return {
                'success': True,
                'message': f'Successfully permanently deleted keyword ID {keyword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error deleting keyword: {e}")
    
    @staticmethod
    def get_keywords_count() -> Dict[str, Any]:
        """Get statistics about keywords"""
        try:
            # Get all keywords
            all_response = supabase_client.client.table('keywords').select('*').execute()
            all_keywords = all_response.data
            
            # Get active keywords
            active_response = supabase_client.client.table('keywords').select('*').eq('is_active', True).execute()
            active_keywords = active_response.data
            
            return {
                'total_keywords': len(all_keywords),
                'active_keywords': len(active_keywords),
                'inactive_keywords': len(all_keywords) - len(active_keywords)
            }
        except Exception as e:
            raise Exception(f"Error getting keyword statistics: {e}") 