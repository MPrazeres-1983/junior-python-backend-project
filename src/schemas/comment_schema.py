"""Comment validation schemas."""

from marshmallow import Schema, fields, validate


class CommentCreateSchema(Schema):
    """Schema for creating a comment."""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )


class CommentUpdateSchema(Schema):
    """Schema for updating a comment."""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000)
    )


class CommentResponseSchema(Schema):
    """Schema for comment response."""
    id = fields.Int(dump_only=True)
    issue_id = fields.Int()
    author_id = fields.Int()
    content = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
