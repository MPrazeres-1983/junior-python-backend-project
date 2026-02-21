"""Integration tests for auth routes."""

import pytest
import json


@pytest.mark.integration
class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123!',
            'role': 'developer'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'data' in data
        assert data['data']['username'] == 'newuser'
        assert data['data']['email'] == 'new@example.com'
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'NewPass123!'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'weak'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'nonexistent',
            'password': 'WrongPass123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['username'] == 'testuser'
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_logout(self, client, auth_headers):
        """Test logout."""
        response = client.post('/api/v1/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'
