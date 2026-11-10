import pytest


@pytest.mark.django_db
def test_openapi_schema_is_generated(api_client):
    response = api_client.get('/api/schema/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_root_redirects_to_swagger_docs(api_client):
    response = api_client.get('/')
    assert response.status_code == 302
    assert response.url == '/api/docs/'


@pytest.mark.django_db
def test_admin_user_list_shows_role_column(client, make_user):
    from django.contrib.auth import get_user_model
    boss = get_user_model().objects.create_superuser(username='root', password='pw-12345-xyz')
    make_user('alice', role='staff')
    client.force_login(boss)
    response = client.get('/admin/accounts/customuser/')
    assert response.status_code == 200
    assert b'column-role' in response.content
