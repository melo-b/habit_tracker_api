import datetime

import pytest
from habits.models import Habit, HabitLog

LOGS_URL = '/api/logs/'
TODAY = datetime.date.today()


@pytest.fixture
def alice(make_user):
    return make_user('alice')


@pytest.fixture
def bob(make_user):
    return make_user('bob')


@pytest.fixture
def alice_habit(alice):
    return Habit.objects.create(user=alice, name='Alice habit')


@pytest.fixture
def bob_habit(bob):
    return Habit.objects.create(user=bob, name='Bob habit')


@pytest.fixture
def bob_log(bob_habit):
    return HabitLog.objects.create(habit=bob_habit, date=TODAY, completed=True)


# --- Creating logs -----------------------------------------------------------

@pytest.mark.django_db
def test_user_can_log_own_habit(client_for, alice, alice_habit):
    response = client_for(alice).post(
        LOGS_URL, {'habit': alice_habit.id, 'date': TODAY.isoformat(), 'completed': True}
    )
    assert response.status_code == 201
    assert HabitLog.objects.get().habit == alice_habit


@pytest.mark.django_db
def test_user_cannot_log_another_users_habit(client_for, alice, bob_habit):
    response = client_for(alice).post(
        LOGS_URL, {'habit': bob_habit.id, 'date': TODAY.isoformat(), 'completed': True}
    )
    assert response.status_code == 400
    assert 'habit' in response.data
    assert HabitLog.objects.count() == 0


@pytest.mark.django_db
def test_staff_cannot_log_another_users_habit(client_for, make_user, bob_habit):
    staff = make_user('staffer', role='staff')
    response = client_for(staff).post(
        LOGS_URL, {'habit': bob_habit.id, 'date': TODAY.isoformat(), 'completed': True}
    )
    assert response.status_code == 400
    assert HabitLog.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_log_any_habit(client_for, make_user, bob_habit):
    admin = make_user('boss', role='admin')
    response = client_for(admin).post(
        LOGS_URL, {'habit': bob_habit.id, 'date': TODAY.isoformat(), 'completed': True}
    )
    assert response.status_code == 201


# --- Updating logs -----------------------------------------------------------

@pytest.mark.django_db
def test_user_cannot_move_own_log_to_another_users_habit(client_for, alice, alice_habit, bob_habit):
    log = HabitLog.objects.create(habit=alice_habit, date=TODAY)
    response = client_for(alice).patch(f'{LOGS_URL}{log.id}/', {'habit': bob_habit.id})
    assert response.status_code == 400
    log.refresh_from_db()
    assert log.habit == alice_habit


@pytest.mark.django_db
def test_user_cannot_update_another_users_log(client_for, alice, bob_log):
    response = client_for(alice).patch(f'{LOGS_URL}{bob_log.id}/', {'completed': False})
    assert response.status_code == 404
    bob_log.refresh_from_db()
    assert bob_log.completed is True


@pytest.mark.django_db
def test_user_cannot_delete_another_users_log(client_for, alice, bob_log):
    response = client_for(alice).delete(f'{LOGS_URL}{bob_log.id}/')
    assert response.status_code == 404
    assert HabitLog.objects.filter(id=bob_log.id).exists()


# --- Reading logs ------------------------------------------------------------

@pytest.mark.django_db
def test_user_cannot_read_another_users_log(client_for, alice, bob_log):
    assert client_for(alice).get(f'{LOGS_URL}{bob_log.id}/').status_code == 404


@pytest.mark.django_db
def test_log_list_only_contains_own_logs(client_for, alice, alice_habit, bob_log):
    own = HabitLog.objects.create(habit=alice_habit, date=TODAY)
    response = client_for(alice).get(LOGS_URL)
    assert response.status_code == 200
    assert [item['id'] for item in response.data['results']] == [own.id]


# --- Staff / admin object permissions ----------------------------------------

@pytest.mark.django_db
def test_staff_can_read_but_not_modify_others_logs(client_for, make_user, bob_log):
    staff = make_user('staffer', role='staff')
    client = client_for(staff)
    assert client.get(f'{LOGS_URL}{bob_log.id}/').status_code == 200
    assert client.patch(f'{LOGS_URL}{bob_log.id}/', {'completed': False}).status_code == 403
    assert client.delete(f'{LOGS_URL}{bob_log.id}/').status_code == 403


@pytest.mark.django_db
def test_admin_can_modify_any_log(client_for, make_user, bob_log):
    admin = make_user('boss', role='admin')
    client = client_for(admin)
    assert client.patch(f'{LOGS_URL}{bob_log.id}/', {'completed': False}).status_code == 200
    assert client.delete(f'{LOGS_URL}{bob_log.id}/').status_code == 204


# --- Validation --------------------------------------------------------------

@pytest.mark.django_db
def test_cannot_log_a_future_date(client_for, alice, alice_habit):
    tomorrow = TODAY + datetime.timedelta(days=1)
    response = client_for(alice).post(
        LOGS_URL, {'habit': alice_habit.id, 'date': tomorrow.isoformat()}
    )
    assert response.status_code == 400
    assert 'date' in response.data


@pytest.mark.django_db
def test_cannot_log_same_habit_twice_on_one_day(client_for, alice, alice_habit):
    HabitLog.objects.create(habit=alice_habit, date=TODAY)
    response = client_for(alice).post(
        LOGS_URL, {'habit': alice_habit.id, 'date': TODAY.isoformat()}
    )
    assert response.status_code == 400
