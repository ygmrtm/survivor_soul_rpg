from flask import Blueprint, jsonify
from backend.services.watchlist_service import WatchlistService
from backend.services.redis_service import RedisService
from datetime import datetime

watchlist_bp = Blueprint('watchlist', __name__)
watchlist_service = WatchlistService()
redis_service = RedisService()

@watchlist_bp.route('/movies', methods=['GET'])
def get_watchlist():
    """Get the complete watchlist."""
    result = watchlist_service.get_watchlist()
    return jsonify(result)


@watchlist_bp.route('/movies/range/<year_from>/<year_to>/<limit>', methods=['GET'])
def get_watchlist_by_year(year_from, year_to, limit):
    limit = int(limit)
    """Get watchlist filtered by year range."""
    # validate year_from and year_to are valid integers
    if not year_from.isdigit() or not year_to.isdigit():
        return jsonify({"error": "Invalid year"}), 400
    year_from = int(year_from)
    year_to = int(year_to)
    if year_from > year_to:
        return jsonify({"error": "Year from must be less than year to"}), 400
    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit:"+limit}), 400        
    result = watchlist_service.get_watchlist_by_year(year_from, year_to, limit)
    return jsonify(result)

@watchlist_bp.route('/movies/estado/<estado>/<limit>', methods=['GET'])
def get_watchlist_by_estado(estado, limit):
    """Get watchlist filtered by status."""
    limit = int(limit)
    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit:"+limit}), 400        
    result = watchlist_service.get_watchlist_by_estado(estado, limit)
    return jsonify(result)

@watchlist_bp.route('/movies/aleatorio/<tamano>', methods=['GET'])
def get_random_suggested_watchlist(tamano):
    """Get a random selection from the watchlist."""
    # validate tamano is a valid integer
    if not tamano.isdigit():
        return jsonify({"error": "Invalid size"}), 400
    else:
        tamano = int(tamano)
    current_week = datetime.now().isocalendar()[1]
    result = watchlist_service.persist_suggested_watchlist(watchlist_service.get_random_suggested_watchlist(tamano), current_week, tamano)
    return jsonify(result)