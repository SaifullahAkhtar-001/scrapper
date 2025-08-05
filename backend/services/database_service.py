from typing import Dict, Any, List
from services.keyword_service import KeywordService

class DatabaseService:
    """Service class for database operations and connection tests"""
    
    @staticmethod
    def test_connection() -> Dict[str, Any]:
        """Test database connection by fetching keywords"""
        try:
            keywords = KeywordService.get_all_keywords()
            return {
                'success': True,
                'message': 'Database connection successful',
                'keywords_count': len(keywords),
                'sample_keywords': [kw['keyword'] for kw in keywords[:3]] if keywords else []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Database connection failed'
            } 