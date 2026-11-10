import datetime

import pytest
from django.db import IntegrityError, transaction
from habits.models import Habit, HabitLog


@pytest.mark.django_db
def test_user_str_includes_username_and_role(make_user):
    assert str(make_user('alice', role='staff')) == 'alice (staff)'


@pytest.mark.django_db
def test_new_users_default_to_user_role():
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.create_user(username='plain', password='x')
    assert user.role == 'user'


@pytest.mark.django_db
def test_habit_and_log_str(make_user):
    habit = Habit.objects.create(user=make_user('alice'), name='Run')
    done = HabitLog.objects.create(habit=habit, date=datetime.date(2026, 1, 1), completed=True)
    pending = HabitLog.objects.create(habit=habit, date=datetime.date(2026, 1, 2))
    assert str(habit) == 'Run - alice'
    assert str(done) == 'Run - 2026-01-01 - Done'
    assert str(pending) == 'Run - 2026-01-02 - Pending'


@pytest.mark.django_db
def test_database_rejects_duplicate_log_for_same_day(make_user):
    habit = Habit.objects.create(user=make_user('alice'), name='Run')
    HabitLog.objects.create(habit=habit, date=datetime.date(2026, 1, 1))
    with pytest.raises(IntegrityError), transaction.atomic():
        HabitLog.objects.create(habit=habit, date=datetime.date(2026, 1, 1))


@pytest.mark.django_db
def test_same_date_allowed_for_different_habits(make_user):
    user = make_user('alice')
    day = datetime.date(2026, 1, 1)
    HabitLog.objects.create(habit=Habit.objects.create(user=user, name='A'), date=day)
    HabitLog.objects.create(habit=Habit.objects.create(user=user, name='B'), date=day)
    assert HabitLog.objects.count() == 2
