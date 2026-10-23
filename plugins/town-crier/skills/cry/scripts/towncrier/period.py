"""Covered period of a digest."""

import calendar
import datetime as dt
from dataclasses import dataclass

UNITS = ("day", "week", "month")
ANCHORS = ("rolling", "calendar")
ONE_DAY = dt.timedelta(days=1)


@dataclass(frozen=True)
class Period:
    """Covered days, both ends included."""

    start: dt.date
    end: dt.date
    unit: str
    length: int
    anchor: str

    def days(self):
        """Every covered day, in order."""
        n = (self.end - self.start).days + 1
        return [self.start + dt.timedelta(days=i) for i in range(n)]

    def as_dict(self):
        """JSON-friendly form."""
        return {"start": self.start.isoformat(), "end": self.end.isoformat(), "unit": self.unit,
                "length": self.length, "anchor": self.anchor, "n_days": len(self.days())}


def add_months(day, months):
    """Same day ``months`` later (negative: earlier), clipped to month end.

    Parameters
    ----------
    day : datetime.date
        Start day.
    months : int
        Months to add.

    Returns
    -------
    datetime.date
        Shifted day.
    """
    years, month0 = divmod(day.month - 1 + months, 12)
    year, month = day.year + years, month0 + 1
    last = calendar.monthrange(year, month)[1]  # month length
    return day.replace(year=year, month=month, day=min(day.day, last))


def resolve_end(end, run_date):
    """Last covered day from the ``period.end`` setting.

    Parameters
    ----------
    end : str or datetime.date or None
        ``yesterday`` (default), ``today`` or a date.
    run_date : datetime.date
        Day of the run.

    Returns
    -------
    datetime.date
        Last covered day.
    """
    if end in (None, "yesterday"):
        return run_date - ONE_DAY
    if end == "today":
        return run_date
    if isinstance(end, dt.date):
        return end
    return dt.date.fromisoformat(str(end))


def rolling_start(end, length, unit):
    """First day of a window of ``length`` units ending on ``end``."""
    if unit == "day":
        return end - dt.timedelta(days=length - 1)
    if unit == "week":
        return end - dt.timedelta(days=7 * length - 1)
    return add_months(end, -length) + ONE_DAY


def calendar_window(run_date, length, unit):
    """Window aligned on calendar boundaries, for scheduled runs.

    Parameters
    ----------
    run_date : datetime.date
        Day of the run.
    length : int
        Units covered.
    unit : str
        ``day``, ``week`` or ``month``.

    Returns
    -------
    tuple of datetime.date
        Start and end, inclusive. Weeks run Monday to Sunday; two weeks
        are half-months (1st-14th, 15th-end); months are calendar months.

    Raises
    ------
    ValueError
        Unsupported length for weeks.
    """
    if unit == "day":
        end = run_date - ONE_DAY
        return end - dt.timedelta(days=length - 1), end
    if unit == "week" and length == 1:
        end = run_date - dt.timedelta(days=run_date.weekday() + 1)  # last Sunday
        return end - dt.timedelta(days=6), end
    if unit == "week" and length == 2:
        if run_date.day >= 15:
            return run_date.replace(day=1), run_date.replace(day=14)  # first half
        prev_end = run_date.replace(day=1) - ONE_DAY
        return prev_end.replace(day=15), prev_end  # second half of last month
    if unit == "month":
        end = run_date.replace(day=1) - ONE_DAY  # end of last month
        return add_months(end.replace(day=1), -(length - 1)), end
    raise ValueError("calendar anchor supports days, 1 or 2 weeks, and months")


def compute_period(run_date, length=1, unit="week", end="yesterday", anchor="rolling"):
    """Covered period.

    Parameters
    ----------
    run_date : datetime.date
        Day of the run.
    length : int
        Number of units.
    unit : {"day", "week", "month"}
        Unit.
    end : str or datetime.date
        Last day for rolling windows: ``yesterday``, ``today`` or a date.
    anchor : {"rolling", "calendar"}
        Rolling: ``length`` units ending on ``end``. Calendar: aligned
        windows ending before the run day (scheduled runs).

    Returns
    -------
    Period
        Covered days.

    Raises
    ------
    ValueError
        Bad unit, length or anchor.
    """
    if unit not in UNITS:
        raise ValueError(f"period.unit must be one of {UNITS}, not {unit!r}")
    if not isinstance(length, int) or length < 1:
        raise ValueError(f"period.length must be an integer >= 1, not {length!r}")
    if anchor not in ANCHORS:
        raise ValueError(f"period.anchor must be one of {ANCHORS}, not {anchor!r}")
    if anchor == "calendar":
        start, last = calendar_window(run_date, length, unit)
    else:
        last = resolve_end(end, run_date)
        start = rolling_start(last, length, unit)
    return Period(start=start, end=last, unit=unit, length=length, anchor=anchor)
