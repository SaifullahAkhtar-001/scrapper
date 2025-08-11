from typing import Dict, Any

class HealthService:
    """Service class for health checks and system status"""
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get basic health status"""
        return {
            'status': 'healthy',
            'service': 'scrapper-backend'
        }
    
    @staticmethod
    def get_home_status() -> Dict[str, Any]:
        """Get home endpoint status"""
        return {
            'message': 'Flask app is running successfully!',
            'status': 'active'
        } 