"""
Error handlers for the Flask wiki application.
Registers handlers for 404, 403, and 500 errors.
"""

from flask import render_template


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return render_template(
            'errors/400.html',
            error=error
        ), 400

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return render_template(
            'errors/403.html',
            error=error
        ), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return render_template(
            'errors/404.html',
            error=error
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        return render_template(
            'errors/500.html',
            error=error
        ), 500

    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors."""
        return render_template(
            'errors/502.html',
            error=error
        ), 502

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        return render_template(
            'errors/503.html',
            error=error
        ), 503
