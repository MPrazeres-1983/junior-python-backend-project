"""Health check routes."""

from flask import Blueprint
from src.utils.responses import success_response, error_response
from src.utils.logger import logger
import os

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns application health status and database connectivity.
    """
    try:
        # Check database connection
        from src.models.base import db
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    health_status = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'service': os.getenv('APP_NAME', 'Issue Tracker API'),
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'database': db_status,
    }
    
    status_code = 200 if db_status == 'healthy' else 503
    
    if status_code == 200:
        return success_response(data=health_status)
    else:
        return error_response(
            message="Service degraded",
            status_code=status_code,
            details=health_status
        )


@health_bp.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint."""
    return success_response(data={'message': 'pong'})
