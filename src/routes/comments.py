"""Comment routes."""

from flask import Blueprint, request
from marshmallow import ValidationError
from src.services import CommentService
from src.schemas import CommentCreateSchema, CommentUpdateSchema, CommentResponseSchema
from src.utils.responses import (
    success_response, error_response, validation_error_response, created_response,
    not_found_response, forbidden_response, no_content_response,
)
from src.utils.pagination import get_pagination_params
from src.middleware import require_auth, get_current_user_id
from src.utils.logger import logger

comments_bp = Blueprint('comments', __name__, url_prefix='/api/v1')
comment_service = CommentService()


@comments_bp.route('/issues/<int:issue_id>/comments', methods=['GET'])
@require_auth
def get_comments(issue_id):
    """Get comments for an issue with pagination."""
    try:
        user_id = get_current_user_id()
        
        # Check access
        from src.services import IssueService
        issue_service = IssueService()
        if not issue_service.can_access_issue(issue_id, user_id):
            return forbidden_response("Access denied")
        
        # Get pagination
        pagination = get_pagination_params()
        
        # Get comments
        from src.repositories import CommentRepository
        repo = CommentRepository()
        result = repo.paginate_by_issue(
            issue_id=issue_id,
            page=pagination['page'],
            per_page=pagination['per_page']
        )
        
        # Serialize
        schema = CommentResponseSchema(many=True)
        data = schema.dump(result['items'])
        
        return success_response(
            data=data,
            meta={
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages']
            }
        )
    
    except Exception as e:
        logger.error(f"Error in get_comments: {str(e)}")
        return error_response("Failed to get comments", status_code=500)


@comments_bp.route('/issues/<int:issue_id>/comments', methods=['POST'])
@require_auth
def create_comment(issue_id):
    """Create a new comment."""
    try:
        user_id = get_current_user_id()
        
        schema = CommentCreateSchema()
        data = schema.load(request.get_json())
        
        comment, error = comment_service.create_comment(
            issue_id=issue_id,
            author_id=user_id,
            content=data['content']
        )
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not a member" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        response_schema = CommentResponseSchema()
        return created_response(data=response_schema.dump(comment))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in create_comment: {str(e)}")
        return error_response("Failed to create comment", status_code=500)


@comments_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@require_auth
def update_comment(comment_id):
    """Update comment."""
    try:
        user_id = get_current_user_id()
        
        schema = CommentUpdateSchema()
        data = schema.load(request.get_json())
        
        comment, error = comment_service.update_comment(
            comment_id=comment_id,
            user_id=user_id,
            content=data['content']
        )
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        response_schema = CommentResponseSchema()
        return success_response(data=response_schema.dump(comment))
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in update_comment: {str(e)}")
        return error_response("Failed to update comment", status_code=500)


@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """Delete comment."""
    try:
        user_id = get_current_user_id()
        
        success, error = comment_service.delete_comment(comment_id, user_id)
        
        if error:
            if "not found" in error.lower():
                return not_found_response(error)
            elif "not authorized" in error.lower():
                return forbidden_response(error)
            return error_response(error, status_code=400)
        
        return no_content_response()
    
    except Exception as e:
        logger.error(f"Error in delete_comment: {str(e)}")
        return error_response("Failed to delete comment", status_code=500)
