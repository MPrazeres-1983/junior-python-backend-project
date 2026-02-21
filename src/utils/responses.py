"""Standardized API response helpers."""

from typing import Any, Dict, Optional, Tuple
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = 200,
    meta: Optional[Dict] = None
) -> Tuple[Dict, int]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        meta: Optional metadata
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    response: Dict[str, Any] = {}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if meta:
        response['meta'] = meta
    
    return response, status_code


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict] = None
) -> Tuple[Dict, int]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
        details: Optional additional error details
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    error_dict: Dict[str, Any] = {
        'message': message,
        'status': status_code,
    }
    
    if error_code:
        error_dict['code'] = error_code
    else:
        # Generate code from status code
        error_dict['code'] = HTTP_STATUS_CODES.get(status_code, 'UNKNOWN_ERROR').upper().replace(' ', '_')
    
    if details:
        error_dict['details'] = details
    
    return {'error': error_dict}, status_code


def validation_error_response(
    errors: Dict[str, Any],
    message: str = "Validation failed"
) -> Tuple[Dict, int]:
    """
    Create a validation error response.
    
    Args:
        errors: Dictionary of validation errors
        message: Error message
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    return error_response(
        message=message,
        status_code=422,
        error_code='VALIDATION_ERROR',
        details={'validation_errors': errors}
    )


def created_response(
    data: Any,
    message: str = "Resource created successfully",
    location: Optional[str] = None
) -> Tuple[Dict, int, Optional[Dict]]:
    """
    Create a 201 Created response.
    
    Args:
        data: Created resource data
        message: Success message
        location: Optional Location header value
    
    Returns:
        Tuple of (response_dict, status_code, headers)
    """
    response, status = success_response(data=data, message=message, status_code=201)
    headers = {'Location': location} if location else None
    return response, status, headers


def no_content_response() -> Tuple[str, int]:
    """
    Create a 204 No Content response.
    
    Returns:
        Tuple of (empty_string, status_code)
    """
    return '', 204


def unauthorized_response(message: str = "Authentication required") -> Tuple[Dict, int]:
    """Create a 401 Unauthorized response."""
    return error_response(message=message, status_code=401, error_code='UNAUTHORIZED')


def forbidden_response(message: str = "Access forbidden") -> Tuple[Dict, int]:
    """Create a 403 Forbidden response."""
    return error_response(message=message, status_code=403, error_code='FORBIDDEN')


def not_found_response(message: str = "Resource not found") -> Tuple[Dict, int]:
    """Create a 404 Not Found response."""
    return error_response(message=message, status_code=404, error_code='NOT_FOUND')


def conflict_response(message: str = "Resource conflict") -> Tuple[Dict, int]:
    """Create a 409 Conflict response."""
    return error_response(message=message, status_code=409, error_code='CONFLICT')


def internal_error_response(message: str = "Internal server error") -> Tuple[Dict, int]:
    """Create a 500 Internal Server Error response."""
    return error_response(message=message, status_code=500, error_code='INTERNAL_ERROR')
