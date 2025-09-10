""" Utilities to do things with dates """
from humanize import ordinal

def long_format_date(datetime):
    """ Return a date in long date format"""
    day = datetime.day
    return datetime.strftime(f"{day}{get_day_suffix(datetime.day)} %B, %Y")

def long_format_date_with_day(datetime):
    """ Return a date in long date format"""
    day = datetime.day
    return datetime.strftime(f"%a {day}{get_day_suffix(datetime.day)} %B")

def day_month_time_from_datetime(datetime):
    """
    Return the Day/Month and Time from a DateTime object as a string, where
    the date is DD MMM format and uses an ordinal for the day.

    :param datetime: models.DateTimeField field
    :return: String of Day/Month and Time
    """
    day_with_suffix = ordinal(datetime.day)
    return "{} {} {:02}:{:02}".format(day_with_suffix, datetime.strftime("%b"), (datetime.hour), (datetime.minute))

def day_month_from_datetime(datetime):
    """
    Return the Day/Month from a DateTime object as a string.

    :param datetime: models.DateTimeField field
    :return: String of Day/Month
    """
    return f"{datetime.day:02}/{datetime.month:02}"


def day_month_year_from_datetime(datetime):
    """
    Return the Day/Month from a DateTime object as a string.

    :param datetime: models.DateTimeField field
    :return: String of Day/Month/Year
    """
    return f"{datetime.day:02}/{datetime.month:02}/{datetime.year:04}"

def formatted_datetime(datetime):
    """
    Return a formatted DateTime object

    :param datetime: models.DateTimeField field
    :return: Date/Time in 'dd-mm-yy hh:mm' format
    """
    return f"{formatted_date(datetime)} {formatted_time(datetime)}"


def formatted_date(datetime):
    """
    Return a formatted DateTime object

    :param datetime: models.DateTimeField field
    :return: Date/Time in 'dd-mm-yy hh:mm' format
    """
    return f"{datetime.strftime('%d-%m-%Y')}"

def formatted_time(datetime):
    """
    Return a formatted DateTime object

    :param datetime: models.DateTimeField field
    :return: Date/Time in 'dd-mm-yy hh:mm' format
    """
    return f"{datetime.strftime('%H:%M')}"

def get_day_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    elif day % 10 == 1:
        return 'st'
    elif day % 10 == 2:
        return 'nd'
    elif day % 10 == 3:
        return 'rd'
    else:
        return 'th'