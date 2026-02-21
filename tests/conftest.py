"""Pytest configuration and fixtures."""

import pytest
from src.app import create_app
from src.models.base import db as _db
from src.models import User, Project, Issue, Label, Comment
import os


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Create a new database session for each test."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db
        _db.session.rollback()
        _db.session.remove()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(db):
    """Create a sample user for testing."""
    from src.services import AuthService
    auth_service = AuthService()
    
    user, _ = auth_service.register(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        role='developer'
    )
    return user


@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers with valid token."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    
    data = response.get_json()
    access_token = data['data']['access_token']
    
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def sample_project(db, sample_user):
    """Create a sample project."""
    from src.services import ProjectService
    project_service = ProjectService()
    
    project, _ = project_service.create_project(
        name='Test Project',
        owner_id=sample_user.id,
        description='A test project'
    )
    return project


@pytest.fixture
def sample_issue(db, sample_project, sample_user):
    """Create a sample issue."""
    from src.services import IssueService
    issue_service = IssueService()
    
    issue, _ = issue_service.create_issue(
        project_id=sample_project.id,
        title='Test Issue',
        reporter_id=sample_user.id,
        description='A test issue',
        priority='medium',
        status='open'
    )
    return issue
