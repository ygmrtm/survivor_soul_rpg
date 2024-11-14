from flask import jsonify

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def handle_api_error(error):
    """Return JSON response for API errors."""
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response
