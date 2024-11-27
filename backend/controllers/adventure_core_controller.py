from flask import Blueprint, jsonify
from backend.services.adventure_service import AdventureService

adventure_bp = Blueprint('adventure', __name__)
adventure_service = AdventureService()

@adventure_bp.route('/<id>/create', methods=['POST'])
def create_adventure(id):
    # Create a new adventure
    result = adventure_service.create_adventure(id)
    return jsonify(result)
@adventure_bp.route('/<id>/execute', methods=['POST'])
def execute_adventure(id):
    # Call the service to execute the adventure
    result = adventure_service.execute_adventure(id)
    return jsonify(result)
