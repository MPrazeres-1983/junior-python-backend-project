"""Global error handlers for the application."""

from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from src.utils.responses import error_response, validation_error_response
from src.utils.logger import logger


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle Marshmallow validation errors."""
        logger.warning(f"Validation error: {error.messages}")
        return validation_error_response(error.messages)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad request: {str(error)}")
        return error_response(
            message=str(error.description) if hasattr(error, 'description') else "Bad request",
            status_code=400
        )
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.warning(f"Unauthorized: {str(error)}")
        return error_response(
            message="Authentication required",
            status_code=401,
            error_code="UNAUTHORIZED"
        )
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.warning(f"Forbidden: {str(error)}")
        return error_response(
            message="Access forbidden",
            status_code=403,
            error_code="FORBIDDEN"
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        return error_response(
            message="Resource not found",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return error_response(
            message="Method not allowed",
            status_code=405,
            error_code="METHOD_NOT_ALLOWED"
        )
    
    @app.errorhandler(409)
    def handle_conflict(error):
        """Handle 409 Conflict errors."""
        logger.warning(f"Conflict: {str(error)}")
        return error_response(
            message=str(error.description) if hasattr(error, 'description') else "Resource conflict",
            status_code=409,
            error_code="CONFLICT"
        )
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        logger.warning(f"Unprocessable entity: {str(error)}")
        return error_response(
            message="Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR"
        )
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors."""
        logger.warning(f"Rate limit exceeded: {str(error)}")
        return error_response(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        
        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = "An internal server error occurred"
        
        return error_response(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error: SQLAlchemyError):
        """Handle SQLAlchemy database errors."""
        logger.error(f"Database error: {str(error)}", exc_info=True)
        
        # Rollback the session
        from src.models.base import db
        db.session.rollback()
        
        # Don't expose database error details in production
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = "A database error occurred"
        
        return error_response(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR"
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle generic HTTP exceptions."""
        return error_response(
            message=error.description or "An error occurred",
            status_code=error.code or 500
        )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        
        # Don't expose error details in production
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = "An unexpected error occurred"
        
        return error_response(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
