from flask import Blueprint, jsonify
from backend.services.stencil_service import StencilService

stencil_bp = Blueprint('stencil', __name__)
stencil_service = StencilService()

@stencil_bp.route('/week/<week_number>', methods=['GET'])
def get_by_week(week_number):
    result = stencil_service.get_by_week(week_number)
    return jsonify(result)
