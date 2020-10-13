from datetime import datetime as d, timezone


def utc_to_local(utc_dt: d) -> d:
    """
    Converts 'datetime' object timezone to UTC (+00:00).

    :param utc_dt: Local datetime object.
    :return: UTC (+00:00) datetime object.
    """
    result = utc_dt.replace(tzinfo=timezone.utc).astimezone()
    return result


def execute_time(start_time) -> str:
    """
    Count time between 'start_time' and current timestamp.

    :param start_time: Start time datetime object.
    :return: Formatted execute time in ms.
    """
    time = int(round((d.timestamp(d.now()) - start_time) * 1000, 0))
    result = f'{time}ms'
    return result
