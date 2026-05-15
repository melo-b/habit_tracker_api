import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpassword123', role='user')

@pytest.fixture
def auth_client(api_client, test_user):
    # This fixture logs the user in and returns a client ready to make authenticated requests
    api_client.force_authenticate(user=test_user)
    return api_client