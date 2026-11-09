import pytest

TOKEN_URL = '/api/token/'
REFRESH_URL = '/api/token/refresh/'


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_habits(api_client):
    response = api_client.get('/api/habits/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_logs(api_client):
    assert api_client.get('/api/logs/').status_code == 401


@pytest.mark.django_db
def test_valid_credentials_return_tokens(api_client, make_user):
    make_user('alice', password='s3cret-pass-123')
    response = api_client.post(TOKEN_URL, {'username': 'alice', 'password': 's3cret-pass-123'})
    assert response.status_code == 200
    assert 'access' in response.data and 'refresh' in response.data


@pytest.mark.django_db
def test_wrong_password_is_rejected(api_client, make_user):
    make_user('alice', password='s3cret-pass-123')
    response = api_client.post(TOKEN_URL, {'username': 'alice', 'password': 'wrong'})
    assert response.status_code == 401


@pytest.mark.django_db
def test_access_token_grants_api_access(api_client, make_user):
    make_user('alice', password='s3cret-pass-123')
    tokens = api_client.post(TOKEN_URL, {'username': 'alice', 'password': 's3cret-pass-123'}).data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    assert api_client.get('/api/habits/').status_code == 200


@pytest.mark.django_db
def test_refresh_token_returns_new_access_token(api_client, make_user):
    make_user('alice', password='s3cret-pass-123')
    tokens = api_client.post(TOKEN_URL, {'username': 'alice', 'password': 's3cret-pass-123'}).data
    response = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']})
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_login_attempts_are_throttled(api_client, make_user):
    make_user('alice', password='s3cret-pass-123')
    payload = {'username': 'alice', 'password': 'wrong'}
    statuses = [api_client.post(TOKEN_URL, payload).status_code for _ in range(21)]
    assert statuses[:20] == [401] * 20
    assert statuses[20] == 429
