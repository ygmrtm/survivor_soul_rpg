from flask import Blueprint, jsonify

adventure_bp = Blueprint('adventure', __name__)

@adventure_bp.route('/adventures', methods=['POST'])
def create_adventure():
    # Create a new adventure
    return jsonify(success=True)

@adventure_bp.route('/adventures/<id>/execute', methods=['POST'])
def execute_adventure(id):
    # Execute an adventure
    return jsonify(success=True)
