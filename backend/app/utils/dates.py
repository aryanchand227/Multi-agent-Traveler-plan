"""Date utility functions."""
from __future__ import annotations

import datetime
from typing import Optional

from dateutil import parser as date_parser


def parse_date(date_str: str | None) -> datetime.date | None:
    """Parse a date string into a date object. Returns None if unparseable."""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str).date()
    except (ValueError, TypeError):
        return None


def calculate_duration_days(start: str | None, end: str | None) -> int | None:
    """Calculate the number of days between two date strings."""
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date and end_date:
        delta = (end_date - start_date).days
        return max(delta, 0)
    return None


def format_date(date: datetime.date | None, fmt: str = "%Y-%m-%d") -> str | None:
    """Format a date object to string."""
    if date:
        return date.strftime(fmt)
    return None


def is_valid_date_range(start: str | None, end: str | None) -> bool:
    """Check if start date is before or equal to end date."""
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date and end_date:
        return start_date <= end_date
    return True  # Can't validate if dates are missing


def get_dates_in_range(start: str, end: str) -> list[str]:
    """Get all dates between start and end (inclusive)."""
    start_date = parse_date(start)
    end_date = parse_date(end)
    if not start_date or not end_date:
        return []
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime("%Y-%m-%d"))
        current += datetime.timedelta(days=1)
    return dates
