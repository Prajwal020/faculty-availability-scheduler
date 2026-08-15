from datetime import datetime, date
from typing import Optional
from zoneinfo import ZoneInfo
from app.core.config import settings


def get_current_time(tz_name: Optional[str] = None) -> datetime:
    """
    Returns the current timezone-aware datetime in the institution's configured timezone.
    Defaults to settings.TIMEZONE (e.g. 'Asia/Kolkata').
    """
    tz = ZoneInfo(tz_name or settings.TIMEZONE)
    return datetime.now(tz)


def get_current_date(tz_name: Optional[str] = None) -> date:
    """
    Returns today's date in the institution's configured timezone.
    """
    return get_current_time(tz_name).date()
