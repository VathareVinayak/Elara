from datetime import datetime, timedelta

#  Calculate difference in days between two dates given as strings without abs.
def date_diff_without_abs(date1: str, date2: str, date_format="%Y-%m-%d") -> str:
    d1 = datetime.strptime(date1, date_format)
    d2 = datetime.strptime(date2, date_format)
    delta = d2 - d1
    return abs(delta.days)

# Add days to a date and return new date string.
def add_days(date: str, days: int, date_format="%Y-%m-%d") -> str:
    d = datetime.strptime(date, date_format)
    new_date = d + timedelta(days=days)
    return new_date.strftime(date_format)

# Calculates the absolute difference in days
def date_diff(date1: str, date2: str, fmt="%Y-%m-%d") -> str:
    """
    Calculates the absolute difference in days between two dates.
    Expects ISO 'YYYY-MM-DD' format by default.
    """
    try:
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        delta = abs((d1 - d2).days)
        return f"The difference between {date1} and {date2} is {delta} days."
    except Exception as e:
        return f"Error calculating date difference: {e}"
