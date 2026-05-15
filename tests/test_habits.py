import pytest
from habits.models import Habit
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_authenticated_user_can_create_habit(auth_client, test_user):
    url = '/api/habits/'
    payload = {
        'name': 'Drink Water',
        'description': 'Drink 8 glasses a day',
        'frequency': 'daily'
    }
    response = auth_client.post(url, payload)
    
    # Assert the habit was created successfully
    assert response.status_code == 201
    assert Habit.objects.count() == 1
    assert Habit.objects.get().user == test_user

@pytest.mark.django_db
def test_user_can_only_see_their_own_habits(api_client, test_user):
    # Create a second user and give them a habit
    other_user = User.objects.create_user(username='other', password='pw')
    Habit.objects.create(user=other_user, name='Other Habit')
    
    # Give the primary test_user a habit
    Habit.objects.create(user=test_user, name='My Habit')
    
    # Authenticate as the primary test_user
    api_client.force_authenticate(user=test_user)
    
    response = api_client.get('/api/habits/')
    
    # Assert the primary user only sees 1 habit (their own), not both
    assert response.status_code == 200
    assert len(response.data['results']) == 1 
    assert response.data['results'][0]['name'] == 'My Habit'