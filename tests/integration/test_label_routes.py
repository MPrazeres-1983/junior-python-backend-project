"""Integration tests for label routes."""

import pytest


@pytest.mark.integration
class TestGetLabels:
    """GET /api/v1/labels"""

    def test_get_labels_authenticated(self, client, auth_headers, sample_label):
        response = client.get('/api/v1/labels', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data

    def test_get_labels_unauthenticated(self, client, sample_label):
        """Labels endpoint has optional auth — should return 200."""
        response = client.get('/api/v1/labels')
        assert response.status_code == 200

    def test_get_labels_empty(self, client):
        response = client.get('/api/v1/labels')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['data'], list)


@pytest.mark.integration
class TestCreateLabel:
    """POST /api/v1/labels — admin only"""

    def test_create_label_success(self, client, admin_headers):
        response = client.post('/api/v1/labels', headers=admin_headers, json={
            'name': 'feature',
            'color': '#00FF00'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['name'] == 'feature'
        assert data['data']['color'] == '#00FF00'

    def test_create_label_default_color(self, client, admin_headers):
        response = client.post('/api/v1/labels', headers=admin_headers, json={
            'name': 'enhancement'
        })
        assert response.status_code == 201

    def test_create_label_duplicate_name(self, client, admin_headers, sample_label):
        response = client.post('/api/v1/labels', headers=admin_headers, json={
            'name': 'bug'  # sample_label is already named 'bug'
        })
        assert response.status_code == 400

    def test_create_label_missing_name(self, client, admin_headers):
        response = client.post('/api/v1/labels', headers=admin_headers, json={
            'color': '#123456'
        })
        assert response.status_code == 422

    def test_create_label_non_admin_forbidden(self, client, auth_headers):
        response = client.post('/api/v1/labels', headers=auth_headers, json={
            'name': 'blocked'
        })
        assert response.status_code == 403

    def test_create_label_unauthenticated(self, client):
        response = client.post('/api/v1/labels', json={'name': 'no-auth'})
        assert response.status_code == 401


@pytest.mark.integration
class TestUpdateLabel:
    """PUT /api/v1/labels/<id> — admin only"""

    def test_update_label_success(self, client, admin_headers, sample_label):
        response = client.put(
            f'/api/v1/labels/{sample_label.id}',
            headers=admin_headers,
            json={'name': 'critical-bug', 'color': '#AA0000'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['name'] == 'critical-bug'

    def test_update_label_not_found(self, client, admin_headers):
        response = client.put(
            '/api/v1/labels/99999',
            headers=admin_headers,
            json={'name': 'ghost'}
        )
        assert response.status_code == 404

    def test_update_label_non_admin_forbidden(self, client, auth_headers, sample_label):
        response = client.put(
            f'/api/v1/labels/{sample_label.id}',
            headers=auth_headers,
            json={'name': 'hacked'}
        )
        assert response.status_code == 403

    def test_update_label_unauthenticated(self, client, sample_label):
        response = client.put(
            f'/api/v1/labels/{sample_label.id}',
            json={'name': 'no-auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestDeleteLabel:
    """DELETE /api/v1/labels/<id> — admin only"""

    def test_delete_label_success(self, client, admin_headers):
        create_resp = client.post('/api/v1/labels', headers=admin_headers, json={
            'name': 'label-to-delete'
        })
        label_id = create_resp.get_json()['data']['id']
        response = client.delete(f'/api/v1/labels/{label_id}', headers=admin_headers)
        assert response.status_code == 204

    def test_delete_label_not_found(self, client, admin_headers):
        response = client.delete('/api/v1/labels/99999', headers=admin_headers)
        assert response.status_code == 404

    def test_delete_label_non_admin_forbidden(self, client, auth_headers, sample_label):
        response = client.delete(
            f'/api/v1/labels/{sample_label.id}',
            headers=auth_headers
        )
        assert response.status_code == 403

    def test_delete_label_unauthenticated(self, client, sample_label):
        response = client.delete(f'/api/v1/labels/{sample_label.id}')
        assert response.status_code == 401
