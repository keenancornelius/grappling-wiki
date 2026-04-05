"""
Flask application entry point for GrapplingWiki
"""

import os
from app import create_app


def main():
    """Initialize and run the Flask application"""
    # Get configuration from environment variable or use default
    config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Create application
    app = create_app(config_name)

    # Run application with debug mode from config
    app.run(debug=app.config.get('DEBUG', False))


if __name__ == '__main__':
    main()
