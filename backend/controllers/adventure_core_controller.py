from flask import Blueprint, jsonify
from backend.services.adventure_service import AdventureService

adventure_bp = Blueprint('adventure', __name__)
adventure_service = AdventureService()

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
@adventure_bp.route('/challenges/<int:week_number>', methods=['POST'])
def create_challenges(week_number):
    # Call the service to create challenges for the specified week
    result = adventure_service.create_challenges(week_number)
    return jsonify(result)

@adventure_bp.route('/challenges/<int:week_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number):
    # Call the service to create challenges for the specified week
    result = adventure_service.evaluate_challenges(week_number)
    return jsonify(result)

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
