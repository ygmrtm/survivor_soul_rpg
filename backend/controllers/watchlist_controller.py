from flask import Blueprint, jsonify
from backend.services.watchlist_service import WatchlistService
from datetime import datetime, timedelta

watchlist_bp = Blueprint('watchlist', __name__)
watchlist_service = WatchlistService()

@watchlist_bp.route('/movies', methods=['GET'])
def get_watchlist():
    """Get the complete watchlist."""
    result = watchlist_service.get_watchlist()
    return jsonify(result)

@watchlist_bp.route('/movies/<year_from>/<year_to>', methods=['GET'])
def get_watchlist_by_year(year_from, year_to):
    """Get watchlist filtered by year range."""
    # validate year_from and year_to are valid integers
    if not year_from.isdigit() or not year_to.isdigit():
        return jsonify({"error": "Invalid year"}), 400
    year_from = int(year_from)
    year_to = int(year_to)
    if year_from > year_to:
        return jsonify({"error": "Year from must be less than year to"}), 400
    result = watchlist_service.get_watchlist_by_year(year_from, year_to)
    return jsonify(result)

@watchlist_bp.route('/movies/estado/<estado>', methods=['GET'])
def get_watchlist_by_estado(estado):
    """Get watchlist filtered by status."""
    result = watchlist_service.get_watchlist_by_estado(estado)
    return jsonify(result)

@watchlist_bp.route('/movies/aleatorio/<tamano>', methods=['GET'])
def get_random_watchlist(tamano):
    """Get a random selection from the watchlist."""
    # validate tamano is a valid integer
    if not tamano.isdigit():
        return jsonify({"error": "Invalid size"}), 400
    tamano = int(tamano)
    current_week = datetime.now().isocalendar()[1]
    result = watchlist_service.persist_suggested_watchlist(watchlist_service.get_random_watchlist(tamano), current_week)
    return jsonify(result)