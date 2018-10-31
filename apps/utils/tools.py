from datetime import datetime, timedelta


def date_range(start: datetime, stop: datetime, step: timedelta):
    """
    迭代时间
    :param start: datetime类型
    :param stop: datetime类型
    :param step: timedelta类型
    :return:
    """
    while start < stop:
        yield start
        start += step
