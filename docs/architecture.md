# Architecture Documentation

## Overview

The Issue Tracker API follows a layered architecture pattern, separating concerns into distinct layers:

```
Client → Routes → Middleware → Services → Repositories → Models → Database
```

## Layers

### 1. Routes Layer (src/routes/)
- **Purpose**: HTTP request handling and routing
- **Responsibilities**:
  - Define API endpoints
  - Parse request data
  - Call appropriate services
  - Return HTTP responses
- **Files**: auth.py, projects.py, issues.py, comments.py, labels.py, health.py

### 2. Middleware Layer (src/middleware/)
- **Purpose**: Cross-cutting concerns
- **Responsibilities**:
  - Authentication (JWT verification)
  - Authorization (role-based access)
  - Error handling
  - Rate limiting
- **Files**: auth_middleware.py, error_handler.py

### 3. Services Layer (src/services/)
- **Purpose**: Business logic
- **Responsibilities**:
  - Implement business rules
  - Coordinate between repositories
  - Handle complex operations
  - Enforce authorization rules
- **Files**: auth_service.py, project_service.py, issue_service.py, label_service.py, comment_service.py

### 4. Repositories Layer (src/repositories/)
- **Purpose**: Data access abstraction
- **Responsibilities**:
  - CRUD operations
  - Database queries
  - Pagination
  - Filtering and sorting
- **Files**: base.py, user_repository.py, project_repository.py, issue_repository.py, etc.

### 5. Models Layer (src/models/)
- **Purpose**: Data models and ORM
- **Responsibilities**:
  - Define database schema
  - Model relationships
  - Data validation at ORM level
- **Files**: user.py, project.py, issue.py, label.py, comment.py, associations.py

## Data Flow

### Example: Creating an Issue

1. **Client Request**
   ```
   POST /api/v1/projects/1/issues
   Body: {title, description, priority}
   Headers: {Authorization: Bearer <token>}
   ```

2. **Route Handler** (issues.py)
   - Validates JWT token
   - Validates request data with schema
   - Extracts user_id from token

3. **Service** (issue_service.py)
   - Checks if user is project member
   - Applies business logic
   - Calls repository

4. **Repository** (issue_repository.py)
   - Creates Issue model
   - Persists to database

5. **Response**
   ```
   201 Created
   Body: {id, title, description, ...}
   ```

## Security Architecture

### Authentication Flow
1. User provides username/password
2. Auth service verifies credentials (bcrypt)
3. Generate JWT access token (15min) + refresh token (7d)
4. Client includes access token in Authorization header
5. Middleware verifies token on protected routes

### Authorization
- **Role-based**: admin, developer, viewer
- **Resource-based**: owner, member, assignee
- Services enforce authorization rules

## Database Schema

### Tables
- **users**: User accounts
- **projects**: Project entities
- **issues**: Issue tracking
- **labels**: Issue categorization
- **comments**: Discussion threads
- **project_members**: User-project membership (many-to-many)
- **assignments**: Issue assignees (many-to-many)
- **issue_labels**: Issue labeling (many-to-many)

### Key Relationships
- User → Projects (one-to-many, as owner)
- Project ← → Users (many-to-many, via project_members)
- Project → Issues (one-to-many)
- Issue ← → Users (many-to-many, via assignments)
- Issue ← → Labels (many-to-many, via issue_labels)
- Issue → Comments (one-to-many)

## Configuration

Configuration is environment-based:
- **Development**: Debug mode, verbose logging, relaxed rate limits
- **Testing**: In-memory DB, fast password hashing, no rate limits
- **Production**: Secure settings, strict validation, monitoring

## Scalability Considerations

### Current Design
- Stateless (JWT), easy horizontal scaling
- Database connection pooling
- Efficient queries with indexes

### Future Improvements
- Redis for caching and session storage
- Message queue for async tasks
- Read replicas for database
- CDN for static assets
