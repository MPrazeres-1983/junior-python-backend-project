"""Pytest configuration and fixtures."""

import pytest
from src.app import create_app
from src.models.base import db as _db
from src.models import User, Project, Issue, Label, Comment
import os


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
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


# ── Users ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_user(db):
    """Create a sample developer user for testing."""
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
def admin_user(db):
    """Create an admin user for testing."""
    from src.services import AuthService
    auth_service = AuthService()
    user, _ = auth_service.register(
        username='adminuser',
        email='admin@example.com',
        password='AdminPass123!',
        role='admin'
    )
    return user


@pytest.fixture
def second_user(db):
    """Create a second developer user for authorization tests."""
    from src.services import AuthService
    auth_service = AuthService()
    user, _ = auth_service.register(
        username='seconduser',
        email='second@example.com',
        password='SecondPass123!',
        role='developer'
    )
    return user


# ── Auth headers ───────────────────────────────────────────────────────────

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers for sample_user (developer)."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    access_token = data['data']['access_token']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin_user."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'adminuser',
        'password': 'AdminPass123!'
    })
    data = response.get_json()
    access_token = data['data']['access_token']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def second_user_headers(client, second_user):
    """Get authentication headers for second_user."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'seconduser',
        'password': 'SecondPass123!'
    })
    data = response.get_json()
    access_token = data['data']['access_token']
    return {'Authorization': f'Bearer {access_token}'}


# ── Domain fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def sample_project(db, sample_user):
    """Create a sample project owned by sample_user."""
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
    """Create a sample issue inside sample_project."""
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


@pytest.fixture
def sample_label(db, admin_user):
    """Create a sample label (requires admin)."""
    from src.services import LabelService
    label_service = LabelService()
    label, _ = label_service.create_label(
        name='bug',
        user_id=admin_user.id,
        color='#FF0000'
    )
    return label


@pytest.fixture
def sample_comment(db, sample_issue, sample_user):
    """Create a sample comment on sample_issue."""
    from src.services import CommentService
    comment_service = CommentService()
    comment, _ = comment_service.create_comment(
        issue_id=sample_issue.id,
        author_id=sample_user.id,
        content='This is a test comment'
    )
    return comment
