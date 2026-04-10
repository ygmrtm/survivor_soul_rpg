from flask import Blueprint, jsonify, request
from backend.services.tournament_service import TournamentService

tournament_bp = Blueprint('tournament', __name__)
tournament_service = TournamentService()

@tournament_bp.route('/<tournament_id>', methods=['GET'])
def get_by_id(tournament_id):
    result = tournament_service.get_by_id(tournament_id)
    return jsonify(result)

@tournament_bp.route('/<tournament_id>', methods=['POST'])
def evaluate_tournaments_by_id(tournament_id):
    result = tournament_service.evaluate_tournament_by_id(tournament_id=tournament_id, full_hp=True)
    ganado = result['tournament']['status'] == 'won' if result['tournament']['status'] else False
    if not ganado:
        result = tournament_service.evaluate_tournament_by_id(tournament_id=tournament_id, full_hp=False)
    return jsonify(result)

@tournament_bp.route('/do/count/<status>', methods=['POST'])
def count_by_status(status):
    if status not in ['created']:
        return jsonify({"error": "Invalid status:"+status}), 400
    count, tournaments = tournament_service.count_n_get_by_status(status=status)
    return jsonify({"count": count , "tournaments": tournaments}), 200    

@tournament_bp.route('/do/exec/<status>/<limit>', methods=['POST'])
def evaluate_tournaments_by_status(status='created', limit=10):
    limit = int(limit)
    if status not in ['created','accepted']:
        return jsonify({"error": "Invalid status:"+status}), 400
    if limit < 1:
        return jsonify({"error": "Invalid limit:"+limit}), 400
    result = tournament_service.evaluate_tournaments_by_status(full_hp=True, status=status, limit=limit)
    return jsonify(result)

@tournament_bp.route('/do/create', methods=['POST'])
def create_tournament():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    description = payload.get("description")
    print(title,description)
    if not title or not description:
        return jsonify({
            "error": "Both 'title' and 'description' are required in JSON payload."
        }), 400

    result = tournament_service.create_tournament(title, description)
    return jsonify(result)

 