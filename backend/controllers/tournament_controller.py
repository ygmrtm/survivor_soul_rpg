from flask import Blueprint, jsonify
from backend.services.tournament_service import TournamentService

tournament_bp = Blueprint('tournament', __name__)
tournament_service = TournamentService()

@tournament_bp.route('/<tournament_id>/show', methods=['GET'])
def get_by_id(tournament_id):
    result = tournament_service.get_by_id(tournament_id)
    return jsonify(result)

@tournament_bp.route('/all', methods=['GET'])
def get_all_open_tournaments():
    result = tournament_service.get_all_open_tournaments()
    return jsonify({'open_tournaments':result, 'pending_tournaments': len(result)})

@tournament_bp.route('/evaluate/all', methods=['GET'])
def evaluate_all_tournaments():
    result = tournament_service.evaluate_all_tournaments(full_hp=True)
    return jsonify(result)

@tournament_bp.route('/create', methods=['POST'])
def create_challenges():
    result = tournament_service.create_tournament('Tournament by Ephemerides','Día del Gato 🐱')
    return jsonify(result)