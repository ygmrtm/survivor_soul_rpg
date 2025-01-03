from flask import Blueprint, jsonify
from backend.services.bike_service import BikeService

bike_bp = Blueprint('bike', __name__)
bike_service = BikeService()

@bike_bp.route('/week/<week_number>', methods=['GET'])
def get_by_week(week_number):
    result = bike_service.get_by_week(week_number)
    return jsonify(result)
