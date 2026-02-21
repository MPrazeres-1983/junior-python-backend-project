"""Routes package - Blueprint registration."""

from flask import Flask
from .auth import auth_bp
from .projects import projects_bp
from .issues import issues_bp
from .comments import comments_bp
from .labels import labels_bp
from .health import health_bp


def register_blueprints(app: Flask) -> None:
    """
    Register all blueprints with the Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(labels_bp)
    app.register_blueprint(health_bp)


__all__ = [
    'register_blueprints',
    'auth_bp',
    'projects_bp',
    'issues_bp',
    'comments_bp',
    'labels_bp',
    'health_bp',
]
