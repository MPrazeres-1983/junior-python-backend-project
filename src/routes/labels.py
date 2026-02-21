"""Label routes."""

from flask import Blueprint
from marshmallow import ValidationError
from src.services import LabelService
from src.schemas import LabelCreateSchema, LabelUpdateSchema, LabelResponseSchema
from src.utils.responses import (
    success_response, error_response, validation_error_response, created_response,
    not_found_response, forbidden_response, no_content_response,
)
from src.middleware import require_auth, require_role, get_current_user_id, optional_auth
from src.utils.logger import logger
from flask import request

labels_bp = Blueprint('labels', __name__, url_prefix='/api/v1/labels')
label_service = LabelService()


@labels_bp.route('', methods=['GET'])
@optional_auth
def get_labels():
    """Get all labels."""
    try:
        labels = label_service.get_all_labels()
        
        schema = LabelResponseSchema(many=True)
        return success_response(data=schema.dump(labels))
    
    except Exception as e:
        logger.error(f"Error in get_labels: {str(e)}")
        return error_response("Failed to get labels", status_code=500)


@labels_bp.route('', methods=['POST'])
@require_role('admin')
def create_label():
    """Create a new label (admin only)."""
    try:
        user_id = get_current_user_id()
        
        schema = LabelCreateSchema()
        data = schema.load(request.get_json())
        
        label, error = label_service.create_label(
            name=data['name'],
            user_id=user_id,
            color=data.get('color', '#808080')
        )
        
        if error:
            return error_response(error, status_code=400)
        
        response_schema = LabelResponseSchema()
        return created_response(data=response_schema.dump(label))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in create_label: {str(e)}")
        return error_response("Failed to create label", status_code=500)


@labels_bp.route('/<int:label_id>', methods=['PUT'])
@require_role('admin')
def update_label(label_id):
    """Update label (admin only)."""
    try:
        user_id = get_current_user_id()
        
        schema = LabelUpdateSchema()
        data = schema.load(request.get_json())
        
        label, error = label_service.update_label(label_id, user_id, **data)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            return error_response(error, status_code=400)
        
        response_schema = LabelResponseSchema()
        return success_response(data=response_schema.dump(label))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in update_label: {str(e)}")
        return error_response("Failed to update label", status_code=500)


@labels_bp.route('/<int:label_id>', methods=['DELETE'])
@require_role('admin')
def delete_label(label_id):
    """Delete label (admin only)."""
    try:
        user_id = get_current_user_id()
        
        success, error = label_service.delete_label(label_id, user_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in delete_label: {str(e)}")
        return error_response("Failed to delete label", status_code=500)
