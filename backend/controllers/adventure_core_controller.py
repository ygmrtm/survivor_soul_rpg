from flask import Blueprint, jsonify
from backend.services.adventure_service import AdventureService
from backend.services.coding_service import CodingService
from backend.services.bike_service import BikingService
from backend.services.stencil_service import StencilService
from backend.services.epics_service import EpicsService

adventure_bp = Blueprint('adventure', __name__)
adventure_service = AdventureService()
coding_service = CodingService()
bike_service = BikingService()
stencil_service = StencilService()
epics_service = EpicsService()

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
                    , "created" : adventures_created
                    , "executed" : adventures_executed
                    , "awaked" : characters_awaked
                    , "punishments" : adventures_punishment})

@adventure_bp.route('/challenges/<int:week_number>/<int:year_number>/create', methods=['POST'])
def create_challenges(week_number, year_number):
    result = adventure_service.create_challenges(week_number, year_number)
    return jsonify(result)

@adventure_bp.route('/challenges/expired/<int:week_number>/<int:year_number>', methods=['POST'])
def evaluate_expired_challenges(week_number, year_number):
    result = adventure_service.evaluate_expired_challenges(week_number, year_number)
    return jsonify(result)

@adventure_bp.route('/challenges/due_soon/<int:lookforward>/', methods=['POST'])
def evaluate_challenges_due_soon(lookforward):
    result = adventure_service.evaluate_challenges_due_soon(lookforward=lookforward)
    return jsonify(result)

@adventure_bp.route('/challenges/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    # Call the service to create challenges for the specified week
    challenges_cons = adventure_service.evaluate_consecutivedays_challenges(week_number, year_number)
    challenges_habits = adventure_service.evaluate_weekhabits_challenges(week_number, year_number)
    challenges_expired = adventure_service.evaluate_expired_challenges(week_number, year_number)
    # Call Specify Ability Challenges
    challenges_coding = coding_service.evaluate_challenges(week_number, year_number)
    challenges_biking = bike_service.evaluate_challenges(week_number, year_number)
    challenges_stencil = stencil_service.evaluate_challenges(week_number, year_number)
    challenges_epics = epics_service.evaluate_challenges(week_number, year_number)
    challenges_due_soon = []#adventure_service.evaluate_challenges_due_soon(lookforward=15)
    return jsonify({"consecutivedays": challenges_cons
                    , "habits": challenges_habits
                    , "expired": challenges_expired
                    , "coding": challenges_coding
                    , "biking": challenges_biking
                    , "stencil": challenges_stencil
                    , "epics": challenges_epics
                    , "due_soon": challenges_due_soon})

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
