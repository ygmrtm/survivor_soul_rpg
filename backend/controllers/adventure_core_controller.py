from flask import Blueprint, jsonify
from backend.services.adventure_service import AdventureService
from backend.services.coding_service import CodingService
from backend.services.bike_service import BikingService
from backend.services.stencil_service import StencilService
from backend.services.epics_service import EpicsService
from backend.services.redis_service import RedisService
from datetime import datetime
import time
import random
adventure_bp = Blueprint('adventure', __name__)
adventure_service = AdventureService()
coding_service = CodingService()
bike_service = BikingService()
stencil_service = StencilService()
epics_service = EpicsService()
redis_service = RedisService()

@adventure_bp.route('/<id>/create', methods=['POST'])
def create_adventure(id):
    # Create a new adventure
    result = adventure_service.create_adventure(id, underworld=False)
    return jsonify(result)

@adventure_bp.route('/<id>/execute', methods=['POST'])
def execute_adventure(id):
    # Call the service to execute the adventure
    result = adventure_service.execute_adventure(id)
    return jsonify(result)

@adventure_bp.route('/underworld', methods=['POST'])
def execute_underworld():
    # Call the service to execute the adventure
    adventure_service = AdventureService()
    adventures_created = []
    adventures_executed = []
    characters_awaked = []
    adventures_punishment = []
    dead_people_count = 0

    adventures_created, dead_people_count = adventure_service.create_underworld_4_deadpeople()
    adventures_executed= adventure_service.execute_underworld()
    characters_awaked = adventure_service.awake_characters()
    adventures_punishment = adventure_service.apply_punishment()
    return jsonify({ "reborn" : len(adventures_executed)
                    , "still_dead" : dead_people_count - len(adventures_executed) 
                    , "created" : adventures_created, "created_count" : len(adventures_created)
                    , "executed" : adventures_executed, "executed_count" : len(adventures_executed)
                    , "awaked" : characters_awaked, "awaked_count" : len(characters_awaked)
                    , "punishments" : adventures_punishment, "punishments_count" : len(adventures_punishment)})

@adventure_bp.route('/challenges/<int:week_number>/<int:year_number>/create', methods=['POST'])
def create_challenges(week_number, year_number):
    result = adventure_service.create_challenges(week_number, year_number)
    return jsonify({"challenges_created":result, "count_challenges":len(result)})

@adventure_bp.route('/challenges/expired/<int:week_number>/<int:year_number>', methods=['POST'])
def evaluate_expired_challenges(week_number, year_number):
    result = adventure_service.evaluate_expired_challenges(week_number, year_number)
    return jsonify(result)

@adventure_bp.route('/challenges/due_soon/<int:lookforward>/', methods=['POST'])
def evaluate_challenges_due_soon(lookforward):
    result = adventure_service.evaluate_challenges_due_soon(lookforward=lookforward)
    return jsonify(result)

@adventure_bp.route('/challenges/not_planned_yet', methods=['POST'])
def evaluate_not_planned_yet():
    result = adventure_service.evaluate_not_planned_yet()
    return jsonify(result)

@adventure_bp.route('/challenges/habit_longest_streak/<int:days_back>', methods=['POST'])
def create_habit_longest_streak(days_back):
    if days_back is None or days_back <= 0:
        periods_back_racha = redis_service.get(redis_service.get_cache_key('num83r5','periods_back_racha'))
        if periods_back_racha is None:
            periods_back_racha = [366, 182, 91, 31]
            redis_service.set_with_expiry(redis_service.get_cache_key('num83r5','periods_back_racha'), periods_back_racha, 24 * 366)        
    else:
        periods_back_racha = [days_back]
    for period in periods_back_racha:
        created = adventure_service.create_habit_longest_streak(last_days=period, create_challenge=False)
    #print("sleeping...")
    #time.sleep(random.randint(30, 60))
    #executed = adventure_service.evaluate_habit_expired_longest_streak(datetime.today().strftime('%Y-%m-%d'))
    #return jsonify({"created":created, "evaluated":executed})
    return jsonify({"created":created})

@adventure_bp.route('/challenges/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    # Call the service to create challenges for the specified week
    days_back_racha = redis_service.get(redis_service.get_cache_key('num83r5','days_back_racha'))
    periods_back_racha = redis_service.get(redis_service.get_cache_key('num83r5','periods_back_racha'))
    if days_back_racha is None:
        days_back_racha = 366
        redis_service.set_with_expiry(redis_service.get_cache_key('num83r5','days_back_racha'), days_back_racha, 24 * days_back_racha)
    if periods_back_racha is None:
        periods_back_racha = [days_back_racha, 182, 91, 31]
        redis_service.set_with_expiry(redis_service.get_cache_key('num83r5','periods_back_racha'), periods_back_racha, 24 * days_back_racha)

    challenges_cons = adventure_service.evaluate_consecutivedays_challenges(week_number, year_number)
    challenges_habits = adventure_service.evaluate_weekhabits_challenges(week_number, year_number)
    challenges_expired = adventure_service.evaluate_expired_challenges(week_number, year_number)
    for period in periods_back_racha:
        habit_longest_streak = adventure_service.create_habit_longest_streak(last_days=period, create_challenge=True)
    habit_longest_streak_executed = adventure_service.evaluate_habit_expired_longest_streak(datetime.today().strftime('%Y-%m-%d'))
    # Call Specify Ability Challenges
    challenges_coding = coding_service.evaluate_challenges(week_number, year_number)
    challenges_biking = bike_service.evaluate_challenges(week_number, year_number)
    challenges_stencil = stencil_service.evaluate_challenges(week_number, year_number)
    challenges_epics = epics_service.evaluate_challenges(week_number, year_number)
    challenges_due_soon = adventure_service.evaluate_challenges_due_soon(lookforward=21)
    return jsonify({"consecutivedays": challenges_cons, "consecutivedays_count" : len(challenges_cons)
                    , "habits": challenges_habits, "challenges_habit_count" : len(challenges_habits)
                    , "habit_longest_streak_created":habit_longest_streak, "habit_longest_streak_created_count": len(habit_longest_streak)
                    , "habit_longest_streak_executed":habit_longest_streak_executed, "habit_longest_streak_executed_count": len(habit_longest_streak_executed)
                    , "expired": challenges_expired, "expired_count": len(challenges_expired)
                    , "coding": challenges_coding, "coding_count": len(challenges_coding)
                    , "biking": challenges_biking, "biking_count": len(challenges_biking)
                    , "stencil": challenges_stencil, "stencil_count": len(challenges_stencil)
                    , "epics": challenges_epics, "epics_count": len(challenges_epics)
                    , "due_soon": challenges_due_soon, "due_soon_count": len(challenges_due_soon)
                    })

@adventure_bp.route('/version', methods=['GET'])
def get_version():
    """Fetch the version number from VERSION.txt."""
    try:
        with open('VERSION.txt', 'r') as version_file:
            version = version_file.read().strip()
        return jsonify({"version": version}), 200
    except FileNotFoundError:
        return jsonify({"error": "Version file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
