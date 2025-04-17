import datetime

def get_current_date():
    """Get the current date."""
    return datetime.datetime.now().date()

def is_data_science_day(date=None):
    """
    Determine if the given date is a Data Science content day.
    Data Science days are Monday (0), Wednesday (2), and Friday (4).
    """
    if date is None:
        date = get_current_date()
    
    # Get the weekday (0 is Monday, 6 is Sunday)
    weekday = date.weekday()
    
    # Return True if it's Monday, Wednesday, or Friday
    return weekday in [0, 2, 4]  # Monday, Wednesday, Friday