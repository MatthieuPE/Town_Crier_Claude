"""Tests of the covered period."""

import datetime as dt

import pytest

from towncrier.period import add_months, compute_period

D = dt.date


@pytest.mark.run
@pytest.mark.period
@pytest.mark.unit
@pytest.mark.parametrize("length, unit, start, end", [
    (1, "week", D(2026, 10, 16), D(2026, 10, 22)),
    (2, "week", D(2026, 10, 9), D(2026, 10, 22)),
    (3, "day", D(2026, 10, 20), D(2026, 10, 22)),
    (1, "month", D(2026, 9, 23), D(2026, 10, 22)),
])
def test_rolling_ends_yesterday(length, unit, start, end):
    """Rolling windows end the day before the run."""
    p = compute_period(D(2026, 10, 23), length=length, unit=unit)
    assert (p.start, p.end) == (start, end)


@pytest.mark.run
@pytest.mark.period
@pytest.mark.unit
@pytest.mark.parametrize("run, length, unit, start, end", [
    (D(2026, 10, 19), 1, "week", D(2026, 10, 12), D(2026, 10, 18)),   # Monday: last Mon-Sun
    (D(2026, 10, 22), 1, "week", D(2026, 10, 12), D(2026, 10, 18)),   # Thursday: same week
    (D(2026, 11, 1), 2, "week", D(2026, 10, 15), D(2026, 10, 31)),    # second half of October
    (D(2026, 11, 15), 2, "week", D(2026, 11, 1), D(2026, 11, 14)),    # first half of November
    (D(2026, 11, 1), 1, "month", D(2026, 10, 1), D(2026, 10, 31)),
    (D(2026, 1, 1), 3, "month", D(2025, 10, 1), D(2025, 12, 31)),
])
def test_calendar_windows(run, length, unit, start, end):
    """Calendar windows tile time with no gap or overlap."""
    p = compute_period(run, length=length, unit=unit, anchor="calendar")
    assert (p.start, p.end) == (start, end)


@pytest.mark.run
@pytest.mark.period
@pytest.mark.unit
def test_add_months_clips_month_end():
    """31 March minus one month is 28 February."""
    assert add_months(D(2026, 3, 31), -1) == D(2026, 2, 28)


@pytest.mark.run
@pytest.mark.period
@pytest.mark.unit
def test_bad_settings_raise():
    """Unsupported units and calendar lengths are rejected."""
    with pytest.raises(ValueError):
        compute_period(D(2026, 10, 23), unit="year")
    with pytest.raises(ValueError):
        compute_period(D(2026, 10, 23), length=3, unit="week", anchor="calendar")


@pytest.mark.run
@pytest.mark.period
@pytest.mark.unit
@pytest.mark.parametrize("run, week_end, start, end", [
    (D(2026, 11, 8), 5, D(2026, 11, 1), D(2026, 11, 7)),    # Sunday run, week ends Saturday
    (D(2026, 11, 9), 5, D(2026, 11, 1), D(2026, 11, 7)),    # delayed to Monday: same week
    (D(2026, 11, 8), 6, D(2026, 10, 26), D(2026, 11, 1)),   # Sunday run, week ends Sunday
])
def test_calendar_week_end(run, week_end, start, end):
    """One-week calendar windows end on the last week_end day before the run."""
    p = compute_period(run, unit="week", anchor="calendar", week_end=week_end)
    assert (p.start, p.end) == (start, end)
