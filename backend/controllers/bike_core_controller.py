from flask import Blueprint, jsonify
from backend.services.bike_service import BikingService

biking_bp = Blueprint('biking', __name__)
biking_service = BikingService()

@biking_bp.route('/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_by_week(week_number, year_number):
    result = biking_service.get_by_week(week_number, year_number)
    return jsonify(result)

@biking_bp.route('/week/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    result = biking_service.evaluate_challenges(week_number, year_number)
    return jsonify(result)