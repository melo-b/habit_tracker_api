import datetime
import warnings

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from habits.models import Habit, HabitLog


def make_habits_with_logs(user, habits, logs_each):
    for h in range(habits):
        habit = Habit.objects.create(user=user, name=f'Habit {h}')
        for d in range(logs_each):
            HabitLog.objects.create(habit=habit, date=datetime.date(2026, 1, 1 + d))


def count_queries(client, url):
    with CaptureQueriesContext(connection) as ctx:
        assert client.get(url).status_code == 200
    return len(ctx)


@pytest.mark.django_db
def test_habit_list_query_count_does_not_grow_with_habits(client_for, alice_user):
    client = client_for(alice_user)
    make_habits_with_logs(alice_user, habits=2, logs_each=2)
    few = count_queries(client, '/api/habits/')

    make_habits_with_logs(alice_user, habits=6, logs_each=2)
    many = count_queries(client, '/api/habits/')

    assert many == few


@pytest.mark.django_db
def test_log_list_query_count_does_not_grow_with_logs(client_for, alice_user):
    client = client_for(alice_user)
    make_habits_with_logs(alice_user, habits=1, logs_each=2)
    few = count_queries(client, '/api/logs/')

    make_habits_with_logs(alice_user, habits=4, logs_each=3)
    many = count_queries(client, '/api/logs/')

    assert many == few


@pytest.mark.django_db
@pytest.mark.parametrize('url', ['/api/habits/', '/api/logs/'])
def test_list_endpoints_are_ordered_so_pagination_is_stable(client_for, alice_user, url):
    make_habits_with_logs(alice_user, habits=2, logs_each=2)
    with warnings.catch_warnings():
        warnings.simplefilter('error')  # UnorderedObjectListWarning becomes a failure
        assert client_for(alice_user).get(url).status_code == 200


@pytest.fixture
def alice_user(make_user):
    return make_user('alice')
