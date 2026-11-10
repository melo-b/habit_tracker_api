import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
REGISTER_URL = '/api/auth/register/'
STRONG_PASSWORD = 'Tr1cky-horse-battery'


@pytest.mark.django_db
def test_register_creates_user_without_exposing_password(api_client):
    response = api_client.post(
        REGISTER_URL,
        {'username': 'newbie', 'email': 'n@example.com', 'password': STRONG_PASSWORD},
    )
    assert response.status_code == 201
    assert response.data['username'] == 'newbie'
    assert 'password' not in response.data
    user = User.objects.get(username='newbie')
    assert user.check_password(STRONG_PASSWORD)
    assert user.password != STRONG_PASSWORD  # stored hashed


@pytest.mark.django_db
def test_registered_user_can_log_in(api_client):
    api_client.post(REGISTER_URL, {'username': 'newbie', 'password': STRONG_PASSWORD})
    response = api_client.post('/api/token/', {'username': 'newbie', 'password': STRONG_PASSWORD})
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
@pytest.mark.parametrize('role', ['admin', 'staff'])
def test_register_ignores_client_supplied_role(api_client, role):
    response = api_client.post(
        REGISTER_URL,
        {'username': 'sneaky', 'password': STRONG_PASSWORD, 'role': role,
         'is_staff': True, 'is_superuser': True},
    )
    assert response.status_code == 201
    user = User.objects.get(username='sneaky')
    assert user.role == 'user'
    assert not user.is_staff and not user.is_superuser


@pytest.mark.django_db
def test_register_rejects_duplicate_username(api_client, make_user):
    make_user('taken')
    response = api_client.post(REGISTER_URL, {'username': 'taken', 'password': STRONG_PASSWORD})
    assert response.status_code == 400
    assert 'username' in response.data


@pytest.mark.django_db
@pytest.mark.parametrize('password', ['short1', '12345678901', 'password123'])
def test_register_rejects_weak_passwords(api_client, password):
    response = api_client.post(REGISTER_URL, {'username': 'newbie', 'password': password})
    assert response.status_code == 400
    assert 'non_field_errors' in response.data or 'password' in response.data
    assert not User.objects.filter(username='newbie').exists()


@pytest.mark.django_db
def test_register_rejects_password_similar_to_username(api_client):
    response = api_client.post(REGISTER_URL, {'username': 'johnsmith99', 'password': 'johnsmith99'})
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_requires_username_and_password(api_client):
    response = api_client.post(REGISTER_URL, {})
    assert response.status_code == 400
    assert 'username' in response.data and 'password' in response.data


@pytest.mark.django_db
def test_register_is_throttled(api_client):
    statuses = [
        api_client.post(REGISTER_URL, {'username': f'user{i}', 'password': STRONG_PASSWORD}).status_code
        for i in range(11)
    ]
    assert statuses[:10] == [201] * 10
    assert statuses[10] == 429
