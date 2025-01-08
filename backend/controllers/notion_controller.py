from flask import Blueprint, jsonify
from backend.services.notion_service import NotionService

notion_bp = Blueprint('notion', __name__)
notion_service = NotionService()

@notion_bp.route('/characters/<id>', methods=['GET'])
def get_character_by_id(id):
    result = notion_service.get_character_by_id(id)
    return jsonify(result)

@notion_bp.route('/countdeadpeople', methods=['GET'])
def countdeadpeople():
    l3_characters = notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=False) + notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=True)
    filtered_characters = [c for c in l3_characters if c['status'] == 'dead']    
    return jsonify({"count": len(filtered_characters)}), 200

@notion_bp.route('/dlychcklst/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_daily_checklist(week_number, year_number):
    result = notion_service.get_daily_checklist(week_number, year_number)
    return jsonify(result)

@notion_bp.route('/characters/<id>', methods=['PUT'])
def update_character(id):
    # Update character details
    return jsonify(success=True)

@notion_bp.route('/characters/deep_level', methods=['GET'])
def get_characters_by_deep_level():
    # Filter characters based on deep level criteria
    return jsonify([])

@notion_bp.route('/characters', methods=['GET'])
def get_all_characters():
    # Retrieve characters via Notion API
    return jsonify([])