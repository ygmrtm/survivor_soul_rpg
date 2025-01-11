import os
from flask import Flask, render_template, jsonify
from backend.controllers.notion_controller import notion_bp
from backend.controllers.adventure_core_controller import adventure_bp
from backend.controllers.todoist_controller import todoist_bp
from backend.controllers.coding_core_controller import coding_bp
from backend.controllers.stencil_core_controller import stencil_bp
from backend.controllers.epics_core_controller import epics_bp
from backend.controllers.bike_core_controller import biking_bp
from backend.utils.error_handling import handle_api_error, APIError
from backend.utils.logger import setup_logger
from backend.services.notion_service import NotionService
import config

# Initialize logger
logger = setup_logger("SurvivorSoulRPG")

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'frontend/templates'))

    # Configuration
    app.config.from_object(config)
    app.logger = logger

    # Register Blueprints for API endpoints
    app.register_blueprint(notion_bp, url_prefix="/api/notion")
    app.register_blueprint(adventure_bp, url_prefix="/api/adventure")
    app.register_blueprint(todoist_bp, url_prefix="/api/todoist")
    app.register_blueprint(coding_bp, url_prefix="/api/coding")
    app.register_blueprint(stencil_bp, url_prefix="/api/stencil")
    app.register_blueprint(epics_bp, url_prefix="/api/epics")
    app.register_blueprint(biking_bp, url_prefix="/api/bike")

    # Error Handling
    app.register_error_handler(APIError, handle_api_error)

    @app.route('/')
    def landing_page():
        """Landing page displaying playable characters."""
        # Initialize the NotionService and retrieve character data
        notion_service = NotionService()
        #
        characters = notion_service.get_characters_by_property('npc', value=False)
        if len(characters) <= 0:
            characters = notion_service.get_characters_by_deep_level(deep_level='l3', is_npc=False) 

        # Mock character data in case the Notion API is empty or unavailable
        if not characters:
            characters = [
                {
                    "name": "Abyssal Warrior",
                    "picture": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrMHIY_JaKsn5g1S5iM7CxgVRjcYh24vK-Pw&s",
                    "level": 3,
                    "coins": 150,
                    "xp": 230,
                    "max_xp": 300,
                    "hp": 80,
                    "max_hp": 100,
                    "attack": 40,
                    "defense": 30,
                    "magic": 25,
                    "inventory": ["Ancient Sword", "Potion of Wisdom", "Shadowscale Armor"]
                },
                {
                    "name": "Void Mage",
                    "picture": "https://wreathsigndesigns.com/cdn/shop/files/creepy-eyeball-3-halloween-wreath-metal-sign-6-circle-191.webp?v=1693294395",
                    "level": 5,
                    "coins": 300,
                    "xp": 450,
                    "max_xp": 500,
                    "hp": 60,
                    "max_hp": 60,
                    "attack": 20,
                    "defense": 20,
                    "magic": 55,
                    "inventory": ["Eldritch Tome", "Mana Elixir", "Phantom Robes"]
                }
                # Add additional characters as needed
            ]
        # Render the landing page with character data
        return render_template("landing.html", characters=characters)

    @app.errorhandler(404)
    def page_not_found(e):
        """Custom 404 page."""
        return jsonify(error="Page not found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Custom 500 page."""
        logger.error(f"Internal server error: {e}")
        return jsonify(error="Internal server error"), 500

    # Debug logging example for startup
    logger.info("Survivor Soul RPG application is starting...")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
