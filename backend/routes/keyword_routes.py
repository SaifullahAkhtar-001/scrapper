from flask import Blueprint, request, jsonify
from services.keyword_service import KeywordService

# Create blueprint for keyword routes
keyword_bp = Blueprint('keywords', __name__, url_prefix='/api/keywords')

@keyword_bp.route('/', methods=['GET'])
def get_keywords():
    """Get all active keywords"""
    try:
        keywords = KeywordService.get_all_keywords()
        return jsonify({
            'success': True,
            'data': keywords,
            'count': len(keywords)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/<int:keyword_id>', methods=['GET'])
def get_keyword(keyword_id):
    """Get a specific keyword by ID"""
    try:
        keyword = KeywordService.get_keyword_by_id(keyword_id)
        if not keyword:
            return jsonify({
                'success': False,
                'error': f'Keyword with ID {keyword_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': keyword
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/', methods=['POST'])
def add_keywords():
    """Add multiple keywords"""
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({
                'success': False,
                'error': 'Request body must contain "keywords" array'
            }), 400
        
        keywords = data['keywords']
        
        if not isinstance(keywords, list):
            return jsonify({
                'success': False,
                'error': 'Keywords must be an array'
            }), 400
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': 'Keywords array cannot be empty'
            }), 400
        
        result = KeywordService.add_keywords(keywords)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/<int:keyword_id>', methods=['PUT'])
def update_keyword(keyword_id):
    """Update a specific keyword"""
    try:
        data = request.get_json()
        
        if not data or 'keyword' not in data:
            return jsonify({
                'success': False,
                'error': 'Request body must contain "keyword" field'
            }), 400
        
        keyword = data['keyword'].strip()
        is_active = data.get('is_active', True)
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': 'Keyword cannot be empty'
            }), 400
        
        result = KeywordService.update_keyword(keyword_id, keyword, is_active)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    """Delete a keyword (soft delete)"""
    try:
        result = KeywordService.delete_keyword(keyword_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/<int:keyword_id>/permanent', methods=['DELETE'])
def hard_delete_keyword(keyword_id):
    """Permanently delete a keyword"""
    try:
        result = KeywordService.hard_delete_keyword(keyword_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/stats', methods=['GET'])
def get_keyword_stats():
    """Get keyword statistics"""
    try:
        stats = KeywordService.get_keywords_count()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@keyword_bp.route('/test', methods=['POST'])
def add_test_keywords():
    """Add test keywords for development"""
    try:
        test_keywords = [
            'vintage cigars',
            'Fonseca cigars',
            'Montecristo cigars',
            'Cuban cigars',
            'empty cigar boxes',
            'vintage cigar boxes',
            'H. Upmann cigars',
            'Partagas cigars'
        ]
        
        result = KeywordService.add_keywords(test_keywords)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 