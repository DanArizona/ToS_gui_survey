# utils.py

from datetime import datetime

def days_seconds_ytd() -> str:
    """
    Returns a string like '165_48293' representing:
    - Days since Jan 1 of the current year
    - Seconds since midnight today
    """
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    start_of_today = datetime(now.year, now.month, now.day)

    days_since_start = (start_of_today - start_of_year).days
    seconds_today = int((now - start_of_today).total_seconds())

    return f"{days_since_start:03}_{seconds_today:05}"
