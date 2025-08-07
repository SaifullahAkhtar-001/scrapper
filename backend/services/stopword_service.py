from typing import List, Dict, Any, Optional
from config.supabase_client import supabase_client

class StopwordService:
    """Service class for stopword CRUD operations"""

    @staticmethod
    def get_all_stopwords() -> List[Dict[str, Any]]:
        """Get all active stopwords"""
        try:
            response = supabase_client.client.table('stopwords').select('*').eq('is_active', True).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Error fetching stopwords: {e}")

    @staticmethod
    def get_stopword_by_id(stopword_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific stopword by ID"""
        try:
            response = supabase_client.client.table('stopwords').select('*').eq('id', stopword_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error fetching stopword: {e}")

    @staticmethod
    def add_stopwords(stopwords: List[str]) -> Dict[str, Any]:
        """Add multiple stopwords"""
        try:
            stopword_data = []
            for stopword in stopwords:
                if stopword.strip():
                    stopword_data.append({
                        'stopword': stopword.strip(),
                        'is_active': True
                    })
            if not stopword_data:
                raise Exception("No valid stopwords provided")
            response = supabase_client.client.table('stopwords').upsert(stopword_data).execute()
            return {
                'success': True,
                'message': f'Successfully added {len(response.data)} stopwords',
                'stopwords_added': len(response.data),
                'data': response.data
            }
        except Exception as e:
            raise Exception(f"Error adding stopwords: {e}")

    @staticmethod
    def update_stopword(stopword_id: int, stopword: str, is_active: bool = True) -> Dict[str, Any]:
        """Update a specific stopword"""
        try:
            existing = StopwordService.get_stopword_by_id(stopword_id)
            if not existing:
                raise Exception(f"Stopword with ID {stopword_id} not found")
            response = supabase_client.client.table('stopwords').update({
                'stopword': stopword.strip(),
                'is_active': is_active
            }).eq('id', stopword_id).execute()
            return {
                'success': True,
                'message': f'Successfully updated stopword ID {stopword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error updating stopword: {e}")

    @staticmethod
    def delete_stopword(stopword_id: int) -> Dict[str, Any]:
        """Soft delete a stopword (set is_active to False)"""
        try:
            existing = StopwordService.get_stopword_by_id(stopword_id)
            if not existing:
                raise Exception(f"Stopword with ID {stopword_id} not found")
            response = supabase_client.client.table('stopwords').update({
                'is_active': False
            }).eq('id', stopword_id).execute()
            return {
                'success': True,
                'message': f'Successfully deleted stopword ID {stopword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error deleting stopword: {e}")

    @staticmethod
    def hard_delete_stopword(stopword_id: int) -> Dict[str, Any]:
        """Permanently delete a stopword from the database"""
        try:
            existing = StopwordService.get_stopword_by_id(stopword_id)
            if not existing:
                raise Exception(f"Stopword with ID {stopword_id} not found")
            response = supabase_client.client.table('stopwords').delete().eq('id', stopword_id).execute()
            return {
                'success': True,
                'message': f'Successfully permanently deleted stopword ID {stopword_id}',
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            raise Exception(f"Error deleting stopword: {e}")

    @staticmethod
    def get_stopwords_count() -> Dict[str, Any]:
        """Get statistics about stopwords"""
        try:
            all_response = supabase_client.client.table('stopwords').select('*').execute()
            all_stopwords = all_response.data
            active_response = supabase_client.client.table('stopwords').select('*').eq('is_active', True).execute()
            active_stopwords = active_response.data
            return {
                'total_stopwords': len(all_stopwords),
                'active_stopwords': len(active_stopwords),
                'inactive_stopwords': len(all_stopwords) - len(active_stopwords)
            }
        except Exception as e:
            raise Exception(f"Error getting stopword statistics: {e}") 