from flask import Blueprint, jsonify
from datetime import datetime, timedelta
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

@notion_bp.route('/countpeoplepills', methods=['GET'])
def countpeoplepills():
    count_people_pills = notion_service.count_people_pills('l3')
    return jsonify({"count": count_people_pills}), 200

@notion_bp.route('/flushredis', methods=['POST'])
def flush_redis_cache():
    characters_del = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('characters','*'))
    indicators_del = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('loaded_characters_*','*'))
    return jsonify({"message": "Redis cache flushed successfully"
                    ,"characters:*": characters_del
                    ,"loaded_characters_*:*": indicators_del
                    ,"characters_del": characters_del
                    ,"indicators_del": indicators_del}
                    ), 200

@notion_bp.route('/characters/applypills/deep_level/<deep_level>', methods=['POST'])
def apply_character_pills(deep_level):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    
    jsonback = {}
    
    for pill_color in ['yellow', 'blue', 'green', 'red', 'orange', 'purple', 'gray', 'brown']:
        result = apply_all_pills(deep_level=deep_level, pill_color=pill_color)
        jsonback[pill_color] = result
    return jsonify(jsonback)

@notion_bp.route('/characters/applypills/<deep_level>/color/<pill_color>', methods=['POST'])
def apply_all_pills(deep_level, pill_color ):
    print(f'💊 {pill_color}')
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400

    if pill_color not in ('yellow', 'blue', 'green', 'red', 'orange', 'purple', 'gray', 'brown'):
        return jsonify({"error": "Invalid pill color"}), 400
    
    result = notion_service.apply_all_pills(deep_level=deep_level, pill_color=pill_color, )
    return result

@notion_bp.route('/dlychcklst/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_daily_checklist(week_number, year_number):
    result = notion_service.get_daily_checklist(week_number, year_number)
    today_date = datetime.now()
    start_date = today_date + timedelta(days=-30) 
    # result = notion_service.get_daily_checklist(week_number, year_number, start_date=start_date, end_date=today_date)
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

@notion_bp.route('/habits/<habits_yn>/abilities/<abilities_yn>', methods=['GET'])
def get_habits_and_abilities(habits_yn, abilities_yn):
    return_dict = {}
    if abilities_yn.startswith('y'):
        abilities = notion_service.get_all_abilities()
        return_dict['abilities'] = abilities
        return_dict['abilities_count'] = len(abilities)
        if len(abilities) > 0:
            return_dict['ability_cache'] = notion_service.get_ability_by_id(abilities[0]['id'])
    if habits_yn.startswith('y'):
        habits = notion_service.get_all_habits()
        return_dict['habits'] = habits
        return_dict['habits_count'] = len(habits)
        if len(habits) > 0:
            return_dict['habit_cache'] = notion_service.get_habit_by_id(habits[0]['id'])
    return jsonify(return_dict)
