from flask import Blueprint, jsonify
from backend.services.ticktick_service import TickTickService

ticktick_bp = Blueprint('ticktick', __name__)

@ticktick_bp.route('/health', methods=['GET'])
def ticktick_health():
    ticktick_service = TickTickService()
    health_status = ticktick_service.healthcheck()
    return jsonify(health_status)

@ticktick_bp.route('/status', methods=['GET'])
def ticktick_status():
    ticktick_service = TickTickService()
    is_connected = ticktick_service.check_connection()
    return jsonify({
        'connected': is_connected,
        'status': 'online' if is_connected else 'offline'
    })


@ticktick_bp.route('/get_projects', methods=['GET'])
def ticktick_get_projects():
    ticktick_service = TickTickService()
    if ticktick_service.check_connection():
        projects = ticktick_service.get_projects()
    return jsonify(projects)