from flask import Blueprint, jsonify
from backend.services.todoist_service import TodoistService

todoist_bp = Blueprint('todoist', __name__) 

@todoist_bp.route('/health', methods=['GET'])
def todoist_health():
    todoist_service = TodoistService()
    health_status = todoist_service.healthcheck()
    return jsonify(health_status)

@todoist_bp.route('/status', methods=['GET'])
def todoist_status():
    todoist_service = TodoistService()
    is_connected = todoist_service.check_connection()
    return jsonify({
        'connected': is_connected,
        'status': 'online' if is_connected else 'offline'
    })


@todoist_bp.route('/get_projects', methods=['GET'])
def todoist_get_projects():
    todoist_service = TodoistService()
    if todoist_service.check_connection():
        projects = todoist_service.get_projects()
    return jsonify(projects)
