"""Integration tests for issue routes."""

import pytest


@pytest.mark.integration
class TestGetIssues:
    """GET /api/v1/projects/<id>/issues"""

    def test_list_issues_success(self, client, auth_headers, sample_project, sample_issue):
        response = client.get(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'meta' in data

    def test_list_issues_no_access(self, client, second_user_headers, sample_project):
        response = client.get(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=second_user_headers
        )
        assert response.status_code == 403

    def test_list_issues_unauthenticated(self, client, sample_project):
        response = client.get(f'/api/v1/projects/{sample_project.id}/issues')
        assert response.status_code == 401

    def test_list_issues_with_filters(self, client, auth_headers, sample_project, sample_issue):
        response = client.get(
            f'/api/v1/projects/{sample_project.id}/issues?status=open&priority=medium',
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_list_issues_pagination(self, client, auth_headers, sample_project, sample_issue):
        response = client.get(
            f'/api/v1/projects/{sample_project.id}/issues?page=1&per_page=10',
            headers=auth_headers
        )
        assert response.status_code == 200


@pytest.mark.integration
class TestCreateIssue:
    """POST /api/v1/projects/<id>/issues"""

    def test_create_issue_success(self, client, auth_headers, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=auth_headers,
            json={
                'title': 'New Bug',
                'description': 'Something is broken',
                'priority': 'high',
                'status': 'open'
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == 'New Bug'
        assert data['data']['priority'] == 'high'

    def test_create_issue_minimal(self, client, auth_headers, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=auth_headers,
            json={'title': 'Minimal Issue'}
        )
        assert response.status_code == 201

    def test_create_issue_missing_title(self, client, auth_headers, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=auth_headers,
            json={'description': 'No title'}
        )
        assert response.status_code == 422

    def test_create_issue_project_not_found(self, client, auth_headers):
        response = client.post(
            '/api/v1/projects/99999/issues',
            headers=auth_headers,
            json={'title': 'Ghost issue'}
        )
        assert response.status_code == 404

    def test_create_issue_not_member(self, client, second_user_headers, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=second_user_headers,
            json={'title': 'Sneaky issue'}
        )
        assert response.status_code == 403

    def test_create_issue_unauthenticated(self, client, sample_project):
        response = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            json={'title': 'No auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestGetIssue:
    """GET /api/v1/issues/<id>"""

    def test_get_issue_success(self, client, auth_headers, sample_issue):
        response = client.get(
            f'/api/v1/issues/{sample_issue.id}',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == sample_issue.id
        assert data['data']['title'] == 'Test Issue'

    def test_get_issue_not_found(self, client, auth_headers):
        response = client.get('/api/v1/issues/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_get_issue_no_access(self, client, second_user_headers, sample_issue):
        response = client.get(
            f'/api/v1/issues/{sample_issue.id}',
            headers=second_user_headers
        )
        assert response.status_code == 403

    def test_get_issue_unauthenticated(self, client, sample_issue):
        response = client.get(f'/api/v1/issues/{sample_issue.id}')
        assert response.status_code == 401


@pytest.mark.integration
class TestUpdateIssue:
    """PUT /api/v1/issues/<id>"""

    def test_update_issue_success(self, client, auth_headers, sample_issue):
        response = client.put(
            f'/api/v1/issues/{sample_issue.id}',
            headers=auth_headers,
            json={'title': 'Updated Title', 'status': 'in_progress'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['status'] == 'in_progress'

    def test_update_issue_not_found(self, client, auth_headers):
        response = client.put(
            '/api/v1/issues/99999',
            headers=auth_headers,
            json={'title': 'Ghost'}
        )
        assert response.status_code == 404

    def test_update_issue_forbidden(self, client, second_user_headers, sample_issue):
        response = client.put(
            f'/api/v1/issues/{sample_issue.id}',
            headers=second_user_headers,
            json={'title': 'Hijacked'}
        )
        assert response.status_code == 403

    def test_update_issue_unauthenticated(self, client, sample_issue):
        response = client.put(
            f'/api/v1/issues/{sample_issue.id}',
            json={'title': 'No auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestDeleteIssue:
    """DELETE /api/v1/issues/<id>"""

    def test_delete_issue_success(self, client, auth_headers, sample_project):
        create_resp = client.post(
            f'/api/v1/projects/{sample_project.id}/issues',
            headers=auth_headers,
            json={'title': 'Issue to delete'}
        )
        issue_id = create_resp.get_json()['data']['id']
        response = client.delete(f'/api/v1/issues/{issue_id}', headers=auth_headers)
        assert response.status_code == 204

    def test_delete_issue_not_found(self, client, auth_headers):
        response = client.delete('/api/v1/issues/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_issue_forbidden(self, client, second_user_headers, sample_issue):
        response = client.delete(
            f'/api/v1/issues/{sample_issue.id}',
            headers=second_user_headers
        )
        assert response.status_code == 403

    def test_delete_issue_unauthenticated(self, client, sample_issue):
        response = client.delete(f'/api/v1/issues/{sample_issue.id}')
        assert response.status_code == 401


@pytest.mark.integration
class TestIssueAssignment:
    """POST/DELETE /api/v1/issues/<id>/assign"""

    def test_assign_user_success(self, client, auth_headers, sample_issue,
                                  sample_project, second_user, second_user_headers):
        # Add second_user to project first
        client.post(
            f'/api/v1/projects/{sample_project.id}/members',
            headers=auth_headers,
            json={'user_id': second_user.id, 'role': 'member'}
        )
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/assign',
            headers=auth_headers,
            json={'user_id': second_user.id}
        )
        assert response.status_code == 201

    def test_assign_user_not_member(self, client, auth_headers, sample_issue, second_user):
        """Cannot assign a user who is not a project member."""
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/assign',
            headers=auth_headers,
            json={'user_id': second_user.id}
        )
        assert response.status_code == 403

    def test_assign_issue_not_found(self, client, auth_headers, second_user):
        response = client.post(
            '/api/v1/issues/99999/assign',
            headers=auth_headers,
            json={'user_id': second_user.id}
        )
        assert response.status_code == 404

    def test_unassign_user_not_found(self, client, auth_headers, sample_issue, second_user):
        response = client.delete(
            f'/api/v1/issues/{sample_issue.id}/assign/{second_user.id}',
            headers=auth_headers
        )
        # User was never assigned — expect 400
        assert response.status_code == 400


@pytest.mark.integration
class TestIssueLabels:
    """POST/DELETE /api/v1/issues/<id>/labels"""

    def test_add_label_to_issue(self, client, auth_headers, sample_issue, sample_label):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/labels',
            headers=auth_headers,
            json={'label_id': sample_label.id}
        )
        assert response.status_code == 201

    def test_add_label_issue_not_found(self, client, auth_headers, sample_label):
        response = client.post(
            '/api/v1/issues/99999/labels',
            headers=auth_headers,
            json={'label_id': sample_label.id}
        )
        assert response.status_code == 404

    def test_add_label_not_found(self, client, auth_headers, sample_issue):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/labels',
            headers=auth_headers,
            json={'label_id': 99999}
        )
        assert response.status_code == 404

    def test_remove_label_from_issue(self, client, auth_headers, sample_issue, sample_label):
        # Add first
        client.post(
            f'/api/v1/issues/{sample_issue.id}/labels',
            headers=auth_headers,
            json={'label_id': sample_label.id}
        )
        # Then remove
        response = client.delete(
            f'/api/v1/issues/{sample_issue.id}/labels/{sample_label.id}',
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_remove_label_not_on_issue(self, client, auth_headers, sample_issue, sample_label):
        response = client.delete(
            f'/api/v1/issues/{sample_issue.id}/labels/{sample_label.id}',
            headers=auth_headers
        )
        assert response.status_code == 400
