import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    """Factory: make_user('alice', role='staff') -> saved user."""
    def _make_user(username, role='user', password='testpassword123'):
        return User.objects.create_user(username=username, password=password, role=role)
    return _make_user


@pytest.fixture
def client_for():
    """Factory: client_for(user) -> APIClient authenticated as that user."""
    def _client_for(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    return _client_for


@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpassword123', role='user')


@pytest.fixture
def auth_client(api_client, test_user):
    # This fixture logs the user in and returns a client ready to make authenticated requests
    api_client.force_authenticate(user=test_user)
    return api_client
