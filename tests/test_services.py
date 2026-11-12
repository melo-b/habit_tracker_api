from datetime import date, timedelta

import pytest
from habits.services import compute_stats

TODAY = date(2026, 11, 18)
LONG_AGO = date(2020, 1, 1)


def days_ago(n):
    return TODAY - timedelta(days=n)


def stats(dates, frequency='daily', created_on=LONG_AGO, window_days=30):
    return compute_stats(
        completed_dates=dates, frequency=frequency, today=TODAY,
        created_on=created_on, window_days=window_days,
    )


# --- Empty / basic -----------------------------------------------------------

def test_no_completions_gives_zeroes():
    result = stats([])
    assert result['current_streak'] == 0
    assert result['longest_streak'] == 0
    assert result['total_completions'] == 0
    assert result['completion_rate'] == 0.0
    assert result['last_completed'] is None


def test_single_completion_today():
    result = stats([TODAY])
    assert result['current_streak'] == 1
    assert result['longest_streak'] == 1
    assert result['total_completions'] == 1
    assert result['last_completed'] == TODAY


# --- Daily streaks -----------------------------------------------------------

def test_consecutive_days_ending_today():
    assert stats([TODAY, days_ago(1), days_ago(2)])['current_streak'] == 3


def test_streak_stays_alive_if_last_completed_yesterday():
    result = stats([days_ago(1), days_ago(2)])
    assert result['current_streak'] == 2


def test_streak_is_broken_after_a_missed_day():
    result = stats([days_ago(2), days_ago(3), days_ago(4)])
    assert result['current_streak'] == 0
    assert result['longest_streak'] == 3


def test_longest_streak_survives_a_gap():
    dates = [days_ago(n) for n in (0, 1, 5, 6, 7, 8)]
    result = stats(dates)
    assert result['current_streak'] == 2
    assert result['longest_streak'] == 4


def test_duplicate_dates_are_counted_once():
    result = stats([TODAY, TODAY, days_ago(1)])
    assert result['current_streak'] == 2
    assert result['total_completions'] == 2


def test_future_dates_are_ignored():
    result = stats([TODAY, TODAY + timedelta(days=1), TODAY + timedelta(days=2)])
    assert result['current_streak'] == 1
    assert result['total_completions'] == 1


def test_streak_across_month_and_year_boundaries():
    dates = [date(2025, 12, 30), date(2025, 12, 31), date(2026, 1, 1), date(2026, 1, 2)]
    result = compute_stats(dates, 'daily', today=date(2026, 1, 2), created_on=LONG_AGO)
    assert result['current_streak'] == 4


# --- Weekly streaks ----------------------------------------------------------

THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())


def test_weekly_consecutive_weeks():
    dates = [THIS_MONDAY, THIS_MONDAY - timedelta(weeks=1), THIS_MONDAY - timedelta(weeks=2)]
    assert stats(dates, 'weekly')['current_streak'] == 3


def test_weekly_multiple_logs_in_one_week_count_once():
    dates = [THIS_MONDAY, THIS_MONDAY + timedelta(days=2)]
    result = stats(dates, 'weekly')
    assert result['current_streak'] == 1
    assert result['longest_streak'] == 1
    assert result['total_completions'] == 2


def test_weekly_sunday_and_next_monday_are_different_weeks():
    sunday = THIS_MONDAY - timedelta(days=1)
    result = stats([sunday, THIS_MONDAY], 'weekly')
    assert result['current_streak'] == 2


def test_weekly_streak_alive_if_last_week_completed():
    last_week = THIS_MONDAY - timedelta(weeks=1)
    assert stats([last_week], 'weekly')['current_streak'] == 1


def test_weekly_streak_broken_after_a_missed_week():
    two_weeks_ago = THIS_MONDAY - timedelta(weeks=2)
    result = stats([two_weeks_ago], 'weekly')
    assert result['current_streak'] == 0
    assert result['longest_streak'] == 1


# --- Completion rate ---------------------------------------------------------

def test_daily_rate_over_window():
    dates = [days_ago(n) for n in (0, 2, 4, 6, 8)]
    assert stats(dates, window_days=10)['completion_rate'] == 0.5


def test_rate_ignores_completions_outside_window():
    dates = [days_ago(0), days_ago(50)]
    assert stats(dates, window_days=10)['completion_rate'] == 0.1


def test_rate_is_clamped_to_habit_creation_date():
    # Habit created 4 days ago -> only 5 days exist (inclusive of today)
    dates = [days_ago(n) for n in range(5)]
    result = stats(dates, created_on=days_ago(4), window_days=30)
    assert result['completion_rate'] == 1.0


def test_rate_for_habit_created_today_with_nothing_logged():
    assert stats([], created_on=TODAY)['completion_rate'] == 0.0


def test_weekly_rate_counts_weeks_not_days():
    # 4-week window starting 3 weeks back: 4 weeks, 2 completed
    dates = [THIS_MONDAY, THIS_MONDAY - timedelta(weeks=2)]
    result = stats(dates, 'weekly', window_days=22)
    assert result['completion_rate'] == 0.5


def test_window_days_must_be_positive():
    with pytest.raises(ValueError):
        stats([], window_days=0)


def test_unknown_frequency_is_rejected():
    with pytest.raises(ValueError):
        stats([], frequency='hourly')
