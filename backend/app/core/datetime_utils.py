"""Datetime utilities with WIB (Western Indonesia Time) support."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config import settings

# WIB is UTC+7
WIB_TZ = ZoneInfo(settings.TIMEZONE)


def now_wib() -> datetime:
    """Get current datetime in WIB timezone."""
    return datetime.now(WIB_TZ)


def now_utc() -> datetime:
    """Get current datetime in UTC."""
    return datetime.now(timezone.utc)


def to_wib(dt: datetime) -> datetime:
    """Convert datetime to WIB timezone."""
    if dt.tzinfo is None:
        # Assume UTC if no timezone
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(WIB_TZ)


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=WIB_TZ)
    return dt.astimezone(timezone.utc)


def format_wib(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime in WIB timezone."""
    return to_wib(dt).strftime(fmt)
