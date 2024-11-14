from flask import Blueprint, jsonify

todoist_bp = Blueprint('todoist', __name__)

@todoist_bp.route('/todoist/task', methods=['POST'])
def create_todoist_task():
    # Create a Todoist task
    return jsonify(success=True)
