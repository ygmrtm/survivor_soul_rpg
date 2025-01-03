from flask import Blueprint, jsonify
from backend.services.epics_service import EpicsService

epics_bp = Blueprint('epics', __name__)
epics_service = EpicsService()

@epics_bp.route('/week/<week_number>', methods=['GET'])
def get_by_week(week_number):
    result = epics_service.get_by_week(week_number)
    return jsonify(result)
