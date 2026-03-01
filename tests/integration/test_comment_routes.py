"""Integration tests for comment routes."""

import pytest


@pytest.mark.integration
class TestGetComments:
    """GET /api/v1/issues/<id>/comments"""

    def test_list_comments_success(self, client, auth_headers, sample_issue, sample_comment):
        response = client.get(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'meta' in data

    def test_list_comments_no_access(self, client, second_user_headers, sample_issue):
        response = client.get(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=second_user_headers
        )
        assert response.status_code == 403

    def test_list_comments_unauthenticated(self, client, sample_issue):
        response = client.get(f'/api/v1/issues/{sample_issue.id}/comments')
        assert response.status_code == 401

    def test_list_comments_pagination(self, client, auth_headers, sample_issue, sample_comment):
        response = client.get(
            f'/api/v1/issues/{sample_issue.id}/comments?page=1&per_page=10',
            headers=auth_headers
        )
        assert response.status_code == 200


@pytest.mark.integration
class TestCreateComment:
    """POST /api/v1/issues/<id>/comments"""

    def test_create_comment_success(self, client, auth_headers, sample_issue):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=auth_headers,
            json={'content': 'This is a new comment'}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['content'] == 'This is a new comment'

    def test_create_comment_missing_content(self, client, auth_headers, sample_issue):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 422

    def test_create_comment_issue_not_found(self, client, auth_headers):
        response = client.post(
            '/api/v1/issues/99999/comments',
            headers=auth_headers,
            json={'content': 'Ghost comment'}
        )
        assert response.status_code == 404

    def test_create_comment_not_member(self, client, second_user_headers, sample_issue):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=second_user_headers,
            json={'content': 'Sneaky comment'}
        )
        assert response.status_code == 403

    def test_create_comment_unauthenticated(self, client, sample_issue):
        response = client.post(
            f'/api/v1/issues/{sample_issue.id}/comments',
            json={'content': 'No auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestUpdateComment:
    """PUT /api/v1/comments/<id>"""

    def test_update_comment_success(self, client, auth_headers, sample_comment):
        response = client.put(
            f'/api/v1/comments/{sample_comment.id}',
            headers=auth_headers,
            json={'content': 'Updated comment content'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['content'] == 'Updated comment content'

    def test_update_comment_not_found(self, client, auth_headers):
        response = client.put(
            '/api/v1/comments/99999',
            headers=auth_headers,
            json={'content': 'Ghost'}
        )
        assert response.status_code == 404

    def test_update_comment_forbidden(self, client, second_user_headers, sample_comment):
        response = client.put(
            f'/api/v1/comments/{sample_comment.id}',
            headers=second_user_headers,
            json={'content': 'Hijacked content'}
        )
        assert response.status_code == 403

    def test_update_comment_unauthenticated(self, client, sample_comment):
        response = client.put(
            f'/api/v1/comments/{sample_comment.id}',
            json={'content': 'No auth'}
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestDeleteComment:
    """DELETE /api/v1/comments/<id>"""

    def test_delete_comment_success(self, client, auth_headers, sample_issue):
        # Create a comment to delete
        create_resp = client.post(
            f'/api/v1/issues/{sample_issue.id}/comments',
            headers=auth_headers,
            json={'content': 'Comment to delete'}
        )
        comment_id = create_resp.get_json()['data']['id']
        response = client.delete(
            f'/api/v1/comments/{comment_id}',
            headers=auth_headers
        )
        assert response.status_code == 204

    def test_delete_comment_not_found(self, client, auth_headers):
        response = client.delete('/api/v1/comments/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_comment_forbidden(self, client, second_user_headers, sample_comment):
        response = client.delete(
            f'/api/v1/comments/{sample_comment.id}',
            headers=second_user_headers
        )
        assert response.status_code == 403

    def test_delete_comment_unauthenticated(self, client, sample_comment):
        response = client.delete(f'/api/v1/comments/{sample_comment.id}')
        assert response.status_code == 401
