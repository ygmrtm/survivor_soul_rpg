from flask import Blueprint, jsonify
from backend.services.coding_service import CodingService

coding_bp = Blueprint('coding', __name__)
coding_service = CodingService()

@coding_bp.route('/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_by_week(week_number, year_number):
    result = coding_service.get_by_week(week_number, year_number)
    return jsonify(result)

@coding_bp.route('/week/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    result = coding_service.evaluate_challenges(week_number, year_number)
    return jsonify(result)
