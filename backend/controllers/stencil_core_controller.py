from flask import Blueprint, jsonify
from backend.services.stencil_service import StencilService

stencil_bp = Blueprint('stencil', __name__)
stencil_service = StencilService()

@stencil_bp.route('/week/<int:week_number>/<int:year_number>', methods=['GET'])
def get_by_week(week_number, year_number):
    result = stencil_service.get_by_week(week_number, year_number)
    return jsonify(result)

@stencil_bp.route('/week/<int:week_number>/<int:year_number>/evaluate', methods=['POST'])
def evaluate_challenges(week_number, year_number):
    result = stencil_service.evaluate_challenges(week_number, year_number)
    return jsonify(result)