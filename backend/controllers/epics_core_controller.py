from flask import Blueprint, jsonify
from backend.services.epics_service import EpicsService

epics_bp = Blueprint('epics', __name__)
epics_service = EpicsService()

@epics_bp.route('/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_by_week(week_number, year_number):
    result = epics_service.get_by_week(week_number, year_number)
    return jsonify(result)

@epics_bp.route('/week/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    result = epics_service.evaluate_challenges(week_number, year_number)
    return jsonify(result)