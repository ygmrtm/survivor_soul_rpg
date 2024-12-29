from flask import Blueprint, jsonify
from backend.services.coding_service import CodingService

coding_bp = Blueprint('coding', __name__)
coding_service = CodingService()

@coding_bp.route('/week/<week_number>', methods=['GET'])
def get_by_week(week_number):
    result = coding_service.get_by_week(week_number)
    return jsonify(result)

@coding_bp.route('/week/<int:week_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number):
    result = coding_service.evaluate_challenges(week_number)
    return jsonify(result)
