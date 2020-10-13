from datetime import datetime as d, timezone


def utc_to_local(utc_dt):
    """
    Convert 'datetime' object timezone to UTC (+00:00)

    Args:
        utc_dt (datetime.datetime): object to convert

    Returns:
        result (datetime.datetime): object converted to UTC timezone
    """
    result = utc_dt.replace(tzinfo=timezone.utc).astimezone()
    return result


def execute_time(start_time):
    """
    Count time between 'start_time' and current timestamp

    Args:
        start_time (float): 'datetime.datetime.timestamp()' object

    Returns:
        result (string): difference between 'datetime.datetime.now()' and 'start_time' in milliseconds
    """
    time = int(round((d.timestamp(d.now()) - start_time) * 1000, 0))
    result = f'{time}ms'
    return result
