from datetime import datetime, timedelta

#  Calculate difference in days between two dates given as strings.
def date_diff(date1: str, date2: str, date_format="%Y-%m-%d") -> int:
    d1 = datetime.strptime(date1, date_format)
    d2 = datetime.strptime(date2, date_format)
    delta = d2 - d1
    return abs(delta.days)
# Add days to a date and return new date string.
def add_days(date: str, days: int, date_format="%Y-%m-%d") -> str:
    d = datetime.strptime(date, date_format)
    new_date = d + timedelta(days=days)
    return new_date.strftime(date_format)
