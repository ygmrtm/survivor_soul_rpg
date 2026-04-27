from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from backend.services.notion_service import NotionService
from backend.services.redis_service import RedisService
from backend.services.adventure_service import AdventureService

notion_bp = Blueprint('notion', __name__)
notion_service = NotionService()
redis_service = RedisService()
adventure_service = AdventureService()

'''
CHARACTERS
'''
@notion_bp.route('/characters/<id>', methods=['GET'])
def get_character_by_id(id):
    character = notion_service.get_character_by_id(id)
    return jsonify(character)

@notion_bp.route('/characters/force/<id>', methods=['GET'])
def get_character_by_id_force(id):
    character = notion_service.get_character_by_id_force(id)
    return jsonify(character)

@notion_bp.route('/characters/<id>', methods=['PUT'])
def update_character(id):
    # Update character details
    character = notion_service.get_character_by_id(id)
    datau = {"properties": { "sanity": {"number": round(int(character['sanity'])*1.2)}, 
                            "coins": {"number": round(float(character['coins'])*1.2)}, 
                            }}   
    notion_service.update_character(character, datau)
    return character

@notion_bp.route('/characters/not_npc/<deep_level>/<limit>', methods=['GET'])
def get_characters_not_npc(deep_level, limit ):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    result = notion_service.get_characters_not_npc(deep_level, limit)
    return jsonify(result)


@notion_bp.route('/characters/deep_level/<deep_level>/<is_npc>', methods=['GET'])
def get_characters_by_deep_level_npc(deep_level, is_npc ):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    if is_npc != 'yes' and is_npc != 'no':
        return jsonify({"error": "Invalid is_npc"}), 400
    result = notion_service.get_characters_by_deep_level_npc_source(deep_level, is_npc == 'yes')
    return jsonify(result)

@notion_bp.route('/characters/deep_level/<deep_level>/<is_npc>/<status>', methods=['GET'])
def get_characters_by_deep_level_npc_and_status(deep_level, is_npc, status ):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    if is_npc != 'yes' and is_npc != 'no':
        return jsonify({"error": "Invalid is_npc"}), 400
    result = notion_service.get_characters_by_deep_level_npc_and_status_source(deep_level, is_npc == 'yes', status)
    return jsonify(result)

@notion_bp.route('/loaddeadpeople/<deep_level>', methods=['GET'])
def loaddeadpeople(deep_level):
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    dead_people = notion_service.get_characters_by_deep_level_status_source(deep_level, status="dead")
    characters_awaked_smoke = adventure_service.awake_characters(limit=48)
    deadventures_executed_smoke = adventure_service.execute_underworld(limit=50)
    deadventures_created_smoke = adventure_service.create_underworld_4_deadpeople(limit=77)
    count_need_underwold_creation = 0
    for zombie in dead_people:
        if not zombie['pending_reborn']:
            count_need_underwold_creation += 1
    dead_ids = [obj['id'] for obj in dead_people if obj['id'] is not None]               
    return jsonify({"count_l3_dead": len(dead_people) 
        , "count_need_underwold_creation":count_need_underwold_creation
        , "count_need_awake":len(characters_awaked_smoke)
        , "count_deadventures_to_execute":len(deadventures_executed_smoke)
        , "count_deadventures_tobe_created":len(deadventures_created_smoke)
        , "dead_people": dead_ids
        }), 200

@notion_bp.route('/loadalivepeople/<deep_level>', methods=['GET'])
def loadalivepeople(deep_level):
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    alive_people = notion_service.get_characters_by_deep_level_status_source(deep_level, status="alive")
    return jsonify({"count": len(alive_people) , "characters": alive_people}), 200

@notion_bp.route('/countdeadpeople/<deep_level>', methods=['POST'])
def countdeadpeople(deep_level):
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    count_dead_people = notion_service.count_dead_people_source(deep_level=deep_level)
    return jsonify({"count": count_dead_people}), 200

@notion_bp.route('/countpeoplepills/<deep_level>', methods=['POST'])
def countpeoplepills(deep_level):
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    count_people_pills = notion_service.count_people_pills_source(deep_level)
    return jsonify({"count": count_people_pills}), 200

@notion_bp.route('/flushredis/cryptids', methods=['POST'])
def flush_redis_cache():
    cryptids_count = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('cryptids','*'))
    deadventures_count = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('deadventures','*'))
    tournamentes_count = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('tournaments','*'))
    sets_count = redis_service.flush_keys_by_pattern(redis_service.get_cache_key('sets','l*','*'))
    return jsonify({"message": "Redis cache flushed successfully"
                    ,"cryptids_count": cryptids_count
                    ,"deadventures_count": deadventures_count
                    ,"tournamentes_count": tournamentes_count
                    ,"sets_count": sets_count
                    }), 200

@notion_bp.route('/characters/applypills/<deep_level>/<limit>', methods=['POST'])
def apply_character_pills(deep_level, limit):
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400
    
    jsonback = {}
    
    for pill_color in ['red','yellow', 'blue', 'green',  'orange', 'purple', 'gray', 'brown', 'pink']:
        result = apply_all_pills(deep_level=deep_level, pill_color=pill_color, limit=limit)
        jsonback[pill_color] = result
    characters_awaked = adventure_service.awake_characters(limit=limit)
    jsonback['awaked'] = characters_awaked
    jsonback['awaked_count'] = len(characters_awaked)
    return jsonify(jsonback)

@notion_bp.route('/characters/applypills/<deep_level>/<pill_color>/<limit>', methods=['POST'])
def apply_all_pills(deep_level, pill_color, limit ):
    print(f'💊 {pill_color}')
    # validate deep_level is valid "l"+int
    if not deep_level.startswith('l'):
        return jsonify({"error": "Invalid deep_level"}), 400

    if pill_color not in ('yellow', 'blue', 'green', 'red', 'orange', 'purple', 'gray', 'brown', 'pink'):
        return jsonify({"error": "Invalid pill color"}), 400
    
    result = notion_service.apply_all_pills(deep_level=deep_level, pill_color=pill_color, limit=limit)
    return result

@notion_bp.route('/characters/applypill/character/<pill_color>/<character_id>', methods=['POST'])
def apply_pill( pill_color ,character_id):
    if pill_color not in ('yellow', 'blue', 'green', 'red', 'orange', 'purple', 'gray', 'brown', 'pink'):
        return jsonify({"error": "Invalid pill color " + pill_color}), 400
    character = notion_service.get_character_by_id(character_id)
    alive_chars = notion_service.get_characters_by_deep_level_npc_and_status_source('l3', True , 'alive')
    result = None
    if character:
        print(f'💊 {pill_color} for {character["name"]}')
        result = notion_service.apply_pill_color_to_character(character, pill_color, alive_chars)
    return result 

@notion_bp.route('/dlychcklst/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_daily_checklist(week_number, year_number):
    result = notion_service.get_daily_checklist(week_number, year_number)
    today_date = datetime.now()
    start_date = today_date + timedelta(days=-30) 
    # result = notion_service.get_daily_checklist(week_number, year_number, start_date=start_date, end_date=today_date)
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
