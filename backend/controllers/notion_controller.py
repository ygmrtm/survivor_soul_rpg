from flask import Blueprint, jsonify
from backend.services.notion_service import NotionService
from backend.services.redis_service import RedisService

notion_bp = Blueprint('notion', __name__)
notion_service = NotionService()
redis_service = RedisService()

@notion_bp.route('/characters/<id>', methods=['GET'])
def get_character_by_id(id):
    result = notion_service.get_character_by_id(id)
    return jsonify(result)

@notion_bp.route('/countdeadpeople', methods=['GET'])
def countdeadpeople():
    count_dead_people = notion_service.count_dead_people('l3')
    return jsonify({"count": count_dead_people}), 200

@notion_bp.route('/flushredis', methods=['POST'])
def flush_redis_cache():
    characters_del = redis_service.flush_keys_by_pattern('characters:*')
    indicators_del = redis_service.flush_keys_by_pattern('loaded_characters_*:*')
    return jsonify({"message": "Redis cache flushed successfully"
                    ,"characters:*": characters_del
                    ,"loaded_characters_*:*": indicators_del}), 200

@notion_bp.route('/dlychcklst/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_daily_checklist(week_number, year_number):
    result = notion_service.get_daily_checklist(week_number, year_number)
    return jsonify(result)

@notion_bp.route('/characters/<id>', methods=['PUT'])
def update_character(id):
    # Update character details
    return jsonify(success=True)

@notion_bp.route('/characters/deep_level/<deep_level>/<is_npc>', methods=['GET'])
def get_characters_by_deep_level(deep_level, is_npc ):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    result = notion_service.get_characters_by_deep_level(deep_level, is_npc == 'yes')
    return jsonify(result)

@notion_bp.route('/characters', methods=['GET'])
def get_all_characters():
    result = notion_service.get_all_raw_characters()
    return jsonify(result)