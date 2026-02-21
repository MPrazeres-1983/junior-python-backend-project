# API Examples

## Authentication

### Register User
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "developer"
  }'
```

**Response (201)**:
```json
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "developer",
    "is_active": true,
    "created_at": "2024-02-20T12:00:00"
  },
  "message": "User registered successfully"
}
```

### Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Response (200)**:
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "developer"
    }
  },
  "message": "Login successful"
}
```

## Projects

### Create Project
```bash
curl -X POST http://localhost:5000/api/v1/projects \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Awesome Project",
    "description": "A project to track awesome features"
  }'
```

**Response (201)**:
```json
{
  "data": {
    "id": 1,
    "name": "My Awesome Project",
    "description": "A project to track awesome features",
    "owner_id": 1,
    "is_active": true,
    "created_at": "2024-02-20T12:00:00",
    "updated_at": "2024-02-20T12:00:00"
  },
  "message": "Project created successfully"
}
```

### List Projects
```bash
curl -X GET "http://localhost:5000/api/v1/projects?page=1&per_page=20" \
  -H "Authorization: Bearer <access_token>"
```

**Response (200)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "My Awesome Project",
      "description": "A project to track awesome features",
      "owner_id": 1,
      "is_active": true,
      "created_at": "2024-02-20T12:00:00"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
```

## Issues

### Create Issue
```bash
curl -X POST http://localhost:5000/api/v1/projects/1/issues \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add user authentication",
    "description": "Implement JWT-based authentication",
    "priority": "high",
    "status": "open"
  }'
```

### Filter Issues
```bash
curl -X GET "http://localhost:5000/api/v1/projects/1/issues?status=open&priority=high&page=1" \
  -H "Authorization: Bearer <access_token>"
```

## Comments

### Add Comment
```bash
curl -X POST http://localhost:5000/api/v1/issues/1/comments \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This looks good, let me review the implementation"
  }'
```

## Error Responses

### 400 Bad Request
```json
{
  "error": {
    "message": "Validation failed",
    "status": 400,
    "code": "VALIDATION_ERROR",
    "details": {
      "validation_errors": {
        "email": ["Not a valid email address"]
      }
    }
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "message": "Invalid or missing authentication token",
    "status": 401,
    "code": "UNAUTHORIZED"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "message": "Access denied",
    "status": 403,
    "code": "FORBIDDEN"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "message": "Project not found",
    "status": 404,
    "code": "NOT_FOUND"
  }
}
```
