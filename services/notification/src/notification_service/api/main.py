"""Flask application for Notification Service."""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any

from .blueprints import notifications, templates
from .blueprints.health import bp as health_bp
from ..exceptions import ValidationError, NotificationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configure CORS - allow all origins as requested
    CORS(app, origins="*")
    
    # Register blueprints
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(notifications.bp, url_prefix='/notifications')
    app.register_blueprint(templates.bp, url_prefix='/templates')
    
    # Global error handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors."""
        logger.error(f"Validation error: {error}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": str(error),
            "details": error.errors if hasattr(error, 'errors') else []
        }), 400
    
    @app.errorhandler(NotificationError)
    def handle_notification_error(error):
        """Handle notification-specific errors."""
        logger.error(f"Notification error: {error}")
        return jsonify({
            "success": False,
            "error": "Notification Error",
            "message": str(error)
        }), 500
    
    @app.errorhandler(Exception)
    def handle_general_error(error):
        """Handle general exceptions."""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint with service information."""
        return jsonify({
            "success": True,
            "service": "Notification Service",
            "version": "1.0.0",
            "status": "operational",
            "endpoints": {
                "health": "/health",
                "notifications": "/notifications",
                "templates": "/templates"
            }
        })
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)