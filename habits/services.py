"""Streak and completion statistics for a habit.

Pure functions: they take plain dates and return plain values, with no database or
request access, so the rules are easy to test and reuse.

A habit is measured in *periods*: a day for daily habits, a Monday-Sunday week for
weekly habits. A period is "done" if it contains at least one completed log.
"""
from datetime import date, timedelta
from typing import Iterable, Optional


def _period_index(day: date, frequency: str) -> int:
    """Map a date to an integer so that consecutive periods differ by exactly 1."""
    if frequency == 'daily':
        return day.toordinal()
    # Ordinal 1 (0001-01-01) is a Monday, so (ordinal - 1) // 7 numbers Mon-Sun weeks.
    return (day.toordinal() - 1) // 7


def _longest_run(periods: set[int]) -> int:
    longest = 0
    for period in periods:
        if period - 1 not in periods:  # start of a run
            length = 1
            while period + length in periods:
                length += 1
            longest = max(longest, length)
    return longest


def _current_run(periods: set[int], current_period: int) -> int:
    # The streak is still alive if the latest period is this one or the one before it
    # (so a streak isn't lost just because today hasn't been logged yet).
    if current_period in periods:
        end = current_period
    elif current_period - 1 in periods:
        end = current_period - 1
    else:
        return 0
    length = 0
    while end - length in periods:
        length += 1
    return length


def compute_stats(
    completed_dates: Iterable[date],
    frequency: str,
    today: date,
    created_on: date,
    window_days: int = 30,
) -> dict:
    """Return streaks, totals and the completion rate over the last `window_days` days.

    The window is clamped to start no earlier than `created_on`, so a new habit isn't
    penalised for days before it existed. Dates after `today` are ignored.
    """
    if frequency not in ('daily', 'weekly'):
        raise ValueError(f"Unsupported frequency: {frequency!r}")
    if window_days < 1:
        raise ValueError("window_days must be at least 1")

    done_dates = {d for d in completed_dates if d <= today}
    periods = {_period_index(d, frequency) for d in done_dates}
    current_period = _period_index(today, frequency)

    window_start = max(today - timedelta(days=window_days - 1), created_on)
    first_period = _period_index(window_start, frequency)
    periods_in_window = max(current_period - first_period + 1, 1)
    done_in_window = sum(1 for p in periods if first_period <= p <= current_period)

    last_completed: Optional[date] = max(done_dates) if done_dates else None

    return {
        'current_streak': _current_run(periods, current_period),
        'longest_streak': _longest_run(periods),
        'total_completions': len(done_dates),
        'completion_rate': round(done_in_window / periods_in_window, 2),
        'last_completed': last_completed,
    }
