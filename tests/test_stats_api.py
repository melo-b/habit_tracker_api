import datetime

import pytest
from django.utils import timezone
from habits.models import Habit, HabitLog


def today():
    return timezone.localdate()


def days_ago(n):
    return today() - datetime.timedelta(days=n)


@pytest.fixture
def alice(make_user):
    return make_user('alice')


@pytest.fixture
def habit(alice):
    return Habit.objects.create(user=alice, name='Read')


@pytest.fixture
def bob_habit(make_user):
    return Habit.objects.create(user=make_user('bob'), name='Bob habit')


def stats_url(h):
    return f'/api/habits/{h.id}/stats/'


def log_today_url(h):
    return f'/api/habits/{h.id}/log-today/'


# --- GET /habits/{id}/stats/ -------------------------------------------------

@pytest.mark.django_db
def test_stats_requires_authentication(api_client, habit):
    assert api_client.get(stats_url(habit)).status_code == 401


@pytest.mark.django_db
def test_stats_for_habit_without_logs(client_for, alice, habit):
    response = client_for(alice).get(stats_url(habit))
    assert response.status_code == 200
    assert response.data['current_streak'] == 0
    assert response.data['longest_streak'] == 0
    assert response.data['total_completions'] == 0
    assert response.data['last_completed'] is None


@pytest.mark.django_db
def test_stats_reflect_logged_completions(client_for, alice, habit):
    for n in (0, 1, 2, 5):
        HabitLog.objects.create(habit=habit, date=days_ago(n), completed=True)

    data = client_for(alice).get(stats_url(habit)).data

    assert data['current_streak'] == 3
    assert data['longest_streak'] == 3
    assert data['total_completions'] == 4
    assert data['last_completed'] == today().isoformat()


@pytest.mark.django_db
def test_stats_ignore_logs_not_marked_completed(client_for, alice, habit):
    HabitLog.objects.create(habit=habit, date=today(), completed=True)
    HabitLog.objects.create(habit=habit, date=days_ago(1), completed=False)

    data = client_for(alice).get(stats_url(habit)).data

    assert data['current_streak'] == 1
    assert data['total_completions'] == 1


@pytest.mark.django_db
def test_weekly_habit_uses_weekly_periods(client_for, alice):
    habit = Habit.objects.create(user=alice, name='Long run', frequency='weekly')
    HabitLog.objects.create(habit=habit, date=today(), completed=True)
    HabitLog.objects.create(habit=habit, date=days_ago(7), completed=True)

    assert client_for(alice).get(stats_url(habit)).data['current_streak'] == 2


@pytest.mark.django_db
def test_stats_response_describes_its_window(client_for, alice, habit):
    data = client_for(alice).get(stats_url(habit), {'days': 7}).data
    assert data['window_days'] == 7
    assert data['frequency'] == 'daily'


@pytest.mark.django_db
@pytest.mark.parametrize('days', ['0', '-3', '366', 'abc'])
def test_stats_rejects_invalid_window(client_for, alice, habit, days):
    response = client_for(alice).get(stats_url(habit), {'days': days})
    assert response.status_code == 400
    assert 'days' in response.data


@pytest.mark.django_db
def test_user_cannot_see_stats_for_another_users_habit(client_for, alice, bob_habit):
    assert client_for(alice).get(stats_url(bob_habit)).status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize('role', ['staff', 'admin'])
def test_privileged_roles_can_read_any_habits_stats(client_for, make_user, bob_habit, role):
    client = client_for(make_user('privileged', role=role))
    assert client.get(stats_url(bob_habit)).status_code == 200


@pytest.mark.django_db
def test_stats_do_not_modify_data(client_for, alice, habit):
    HabitLog.objects.create(habit=habit, date=today(), completed=True)
    client_for(alice).get(stats_url(habit))
    assert HabitLog.objects.count() == 1


@pytest.mark.django_db
def test_stats_is_get_only(client_for, alice, habit):
    assert client_for(alice).post(stats_url(habit)).status_code == 405


# --- POST /habits/{id}/log-today/ --------------------------------------------

@pytest.mark.django_db
def test_log_today_requires_authentication(api_client, habit):
    assert api_client.post(log_today_url(habit)).status_code == 401


@pytest.mark.django_db
def test_log_today_creates_a_completed_log(client_for, alice, habit):
    response = client_for(alice).post(log_today_url(habit))
    assert response.status_code == 201
    assert response.data['completed'] is True
    log = HabitLog.objects.get()
    assert log.habit == habit and log.date == today() and log.completed


@pytest.mark.django_db
def test_log_today_is_idempotent(client_for, alice, habit):
    client = client_for(alice)
    first = client.post(log_today_url(habit))
    second = client.post(log_today_url(habit))
    assert first.status_code == 201
    assert second.status_code == 200
    assert HabitLog.objects.count() == 1


@pytest.mark.django_db
def test_log_today_completes_an_existing_pending_log(client_for, alice, habit):
    HabitLog.objects.create(habit=habit, date=today(), completed=False, notes='planned')
    response = client_for(alice).post(log_today_url(habit))
    assert response.status_code == 200
    log = HabitLog.objects.get()
    assert log.completed is True
    assert log.notes == 'planned'  # untouched when not supplied


@pytest.mark.django_db
def test_log_today_accepts_notes_and_completed_flag(client_for, alice, habit):
    response = client_for(alice).post(
        log_today_url(habit), {'completed': False, 'notes': 'skipped, travelling'}
    )
    assert response.status_code == 201
    log = HabitLog.objects.get()
    assert log.completed is False
    assert log.notes == 'skipped, travelling'


@pytest.mark.django_db
def test_log_today_only_touches_todays_log(client_for, alice, habit):
    HabitLog.objects.create(habit=habit, date=days_ago(1), completed=False)
    client_for(alice).post(log_today_url(habit))
    assert HabitLog.objects.get(date=days_ago(1)).completed is False
    assert HabitLog.objects.count() == 2


@pytest.mark.django_db
def test_log_today_updates_streak(client_for, alice, habit):
    HabitLog.objects.create(habit=habit, date=days_ago(1), completed=True)
    client = client_for(alice)
    client.post(log_today_url(habit))
    assert client.get(stats_url(habit)).data['current_streak'] == 2


@pytest.mark.django_db
def test_user_cannot_log_today_for_another_users_habit(client_for, alice, bob_habit):
    assert client_for(alice).post(log_today_url(bob_habit)).status_code == 404
    assert HabitLog.objects.count() == 0


@pytest.mark.django_db
def test_staff_cannot_log_today_for_another_users_habit(client_for, make_user, bob_habit):
    staff = make_user('staffer', role='staff')
    assert client_for(staff).post(log_today_url(bob_habit)).status_code == 403
    assert HabitLog.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_log_today_for_any_habit(client_for, make_user, bob_habit):
    admin = make_user('boss', role='admin')
    assert client_for(admin).post(log_today_url(bob_habit)).status_code == 201


@pytest.mark.django_db
def test_log_today_rejects_non_boolean_completed(client_for, alice, habit):
    response = client_for(alice).post(log_today_url(habit), {'completed': 'maybe'})
    assert response.status_code == 400
    assert HabitLog.objects.count() == 0


# --- Efficiency and docs -----------------------------------------------------

@pytest.mark.django_db
def test_stats_query_count_does_not_grow_with_logs(client_for, alice, habit):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    client = client_for(alice)
    HabitLog.objects.create(habit=habit, date=today(), completed=True)
    with CaptureQueriesContext(connection) as few:
        client.get(stats_url(habit))

    for n in range(1, 40):
        HabitLog.objects.create(habit=habit, date=days_ago(n), completed=True)
    with CaptureQueriesContext(connection) as many:
        client.get(stats_url(habit))

    assert len(many) == len(few)


@pytest.mark.django_db
def test_new_endpoints_are_documented_in_openapi_schema(api_client):
    response = api_client.get('/api/schema/', {'format': 'json'})
    assert response.status_code == 200
    paths = response.json()['paths']
    assert 'get' in paths['/api/habits/{id}/stats/']
    assert 'post' in paths['/api/habits/{id}/log-today/']
    assert 'days' in str(paths['/api/habits/{id}/stats/']['get']['parameters'])
