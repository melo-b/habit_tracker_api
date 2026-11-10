import pytest
from django.utils import timezone
from habits.models import Habit, HabitLog

HABITS_URL = '/api/habits/'


def detail(habit):
    return f'{HABITS_URL}{habit.id}/'


@pytest.fixture
def alice(make_user):
    return make_user('alice')


@pytest.fixture
def bob(make_user):
    return make_user('bob')


@pytest.fixture
def bob_habit(bob):
    return Habit.objects.create(user=bob, name='Bob habit')


# --- Create ------------------------------------------------------------------

@pytest.mark.django_db
def test_authenticated_user_can_create_habit(auth_client, test_user):
    payload = {'name': 'Drink Water', 'description': 'Drink 8 glasses a day', 'frequency': 'daily'}
    response = auth_client.post(HABITS_URL, payload)

    assert response.status_code == 201
    assert Habit.objects.count() == 1
    assert Habit.objects.get().user == test_user


@pytest.mark.django_db
def test_created_habit_ignores_client_supplied_user(client_for, alice, bob):
    response = client_for(alice).post(HABITS_URL, {'name': 'Mine', 'user': bob.id})
    assert response.status_code == 201
    assert Habit.objects.get().user == alice


@pytest.mark.django_db
def test_frequency_defaults_to_daily(client_for, alice):
    response = client_for(alice).post(HABITS_URL, {'name': 'Stretch'})
    assert response.status_code == 201
    assert response.data['frequency'] == 'daily'


@pytest.mark.django_db
def test_invalid_frequency_is_rejected(client_for, alice):
    response = client_for(alice).post(HABITS_URL, {'name': 'Stretch', 'frequency': 'hourly'})
    assert response.status_code == 400
    assert 'frequency' in response.data


@pytest.mark.django_db
def test_name_is_required(client_for, alice):
    response = client_for(alice).post(HABITS_URL, {'description': 'no name'})
    assert response.status_code == 400
    assert 'name' in response.data


# --- Visibility --------------------------------------------------------------

@pytest.mark.django_db
def test_user_can_only_see_their_own_habits(api_client, test_user, bob):
    Habit.objects.create(user=bob, name='Other Habit')
    Habit.objects.create(user=test_user, name='My Habit')
    api_client.force_authenticate(user=test_user)

    response = api_client.get(HABITS_URL)

    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == 'My Habit'


@pytest.mark.django_db
@pytest.mark.parametrize('role', ['staff', 'admin'])
def test_privileged_roles_see_all_habits(client_for, make_user, alice, bob_habit, role):
    Habit.objects.create(user=alice, name='Alice habit')
    privileged = make_user('privileged', role=role)
    response = client_for(privileged).get(HABITS_URL)
    assert response.status_code == 200
    assert response.data['count'] == 2


@pytest.mark.django_db
def test_user_cannot_retrieve_another_users_habit(client_for, alice, bob_habit):
    assert client_for(alice).get(detail(bob_habit)).status_code == 404


# --- Update / delete: role matrix --------------------------------------------

@pytest.mark.django_db
def test_owner_can_update_and_delete_own_habit(client_for, bob, bob_habit):
    client = client_for(bob)
    assert client.patch(detail(bob_habit), {'name': 'Renamed'}).status_code == 200
    bob_habit.refresh_from_db()
    assert bob_habit.name == 'Renamed'
    assert client.delete(detail(bob_habit)).status_code == 204
    assert Habit.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_update_or_delete_another_users_habit(client_for, alice, bob_habit):
    client = client_for(alice)
    assert client.patch(detail(bob_habit), {'name': 'Hacked'}).status_code == 404
    assert client.delete(detail(bob_habit)).status_code == 404
    bob_habit.refresh_from_db()
    assert bob_habit.name == 'Bob habit'


@pytest.mark.django_db
def test_staff_can_read_but_not_modify_others_habits(client_for, make_user, bob_habit):
    client = client_for(make_user('staffer', role='staff'))
    assert client.get(detail(bob_habit)).status_code == 200
    assert client.patch(detail(bob_habit), {'name': 'Hacked'}).status_code == 403
    assert client.delete(detail(bob_habit)).status_code == 403
    assert Habit.objects.filter(id=bob_habit.id, name='Bob habit').exists()


@pytest.mark.django_db
def test_staff_can_modify_own_habit(client_for, make_user):
    staff = make_user('staffer', role='staff')
    habit = Habit.objects.create(user=staff, name='Staff habit')
    assert client_for(staff).patch(detail(habit), {'name': 'Renamed'}).status_code == 200


@pytest.mark.django_db
def test_admin_can_modify_and_delete_any_habit(client_for, make_user, bob_habit):
    client = client_for(make_user('boss', role='admin'))
    assert client.patch(detail(bob_habit), {'name': 'Edited by admin'}).status_code == 200
    assert client.delete(detail(bob_habit)).status_code == 204


@pytest.mark.django_db
def test_update_cannot_reassign_habit_owner(client_for, alice, bob):
    habit = Habit.objects.create(user=alice, name='Mine')
    response = client_for(alice).patch(detail(habit), {'user': bob.id})
    assert response.status_code == 200
    habit.refresh_from_db()
    assert habit.user == alice


# --- List behaviour ----------------------------------------------------------

@pytest.mark.django_db
def test_list_is_paginated_in_pages_of_ten(client_for, alice):
    for i in range(12):
        Habit.objects.create(user=alice, name=f'Habit {i:02d}')
    client = client_for(alice)

    first = client.get(HABITS_URL)
    second = client.get(HABITS_URL, {'page': 2})

    assert first.data['count'] == 12
    assert len(first.data['results']) == 10
    assert len(second.data['results']) == 2


@pytest.mark.django_db
def test_search_matches_name_and_description(client_for, alice):
    Habit.objects.create(user=alice, name='Read books', description='fiction')
    Habit.objects.create(user=alice, name='Run', description='morning cardio')
    client = client_for(alice)

    by_name = client.get(HABITS_URL, {'search': 'read'})
    by_description = client.get(HABITS_URL, {'search': 'cardio'})

    assert [h['name'] for h in by_name.data['results']] == ['Read books']
    assert [h['name'] for h in by_description.data['results']] == ['Run']


@pytest.mark.django_db
def test_search_never_returns_other_users_habits(client_for, alice, bob_habit):
    response = client_for(alice).get(HABITS_URL, {'search': 'Bob'})
    assert response.data['count'] == 0


@pytest.mark.django_db
def test_ordering_by_name(client_for, alice):
    for name in ['Charlie', 'Alpha', 'Bravo']:
        Habit.objects.create(user=alice, name=name)
    client = client_for(alice)

    ascending = [h['name'] for h in client.get(HABITS_URL, {'ordering': 'name'}).data['results']]
    descending = [h['name'] for h in client.get(HABITS_URL, {'ordering': '-name'}).data['results']]

    assert ascending == ['Alpha', 'Bravo', 'Charlie']
    assert descending == ['Charlie', 'Bravo', 'Alpha']


@pytest.mark.django_db
def test_habit_includes_nested_logs(client_for, alice):
    habit = Habit.objects.create(user=alice, name='Meditate')
    HabitLog.objects.create(habit=habit, date=timezone.localdate(), completed=True)

    response = client_for(alice).get(detail(habit))

    assert len(response.data['logs']) == 1
    assert response.data['logs'][0]['completed'] is True


@pytest.mark.django_db
def test_deleting_habit_deletes_its_logs(client_for, alice):
    habit = Habit.objects.create(user=alice, name='Meditate')
    HabitLog.objects.create(habit=habit, date=timezone.localdate())
    client_for(alice).delete(detail(habit))
    assert HabitLog.objects.count() == 0
