import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_habits(api_client):
    url = '/api/habits/'
    response = api_client.get(url)
    
    # Assert that the API blocks the request with a 401 Unauthorized
    assert response.status_code == 401