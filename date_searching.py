from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_date_x_periods_from_today(delta, period):
    """
    Gets a date which was x periods (days, weeks, months, years) from today. Weeks, months, and years are relative.
    Relative means, that if we want 2 months from date 01.03.2023, it returns the same day of 2 months ago (01.01.2023).
    :param delta: int, x periods from today
    :param period: srt, either "d", "wk", "mo", "yr".
    :return: datetime, a date that was x periods ago from today.
    """
    today = datetime.now()
    if period == 'd':
        one_year_ago = today - timedelta(days=delta)
    elif period == 'wk':
        one_year_ago = today - relativedelta(weeks=delta)
    elif period == "mo":
        one_year_ago = today - relativedelta(months=delta)
    elif period == "yr":
        one_year_ago = today - relativedelta(years=delta)
    else:
        raise ValueError("Invalid unit. Supported units are 'd', 'wk', 'mo', and 'yr")
    return one_year_ago
