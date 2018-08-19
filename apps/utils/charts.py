import random
import pickle
from datetime import datetime, timedelta

from django.core.cache import cache

from pyecharts import Line
from users.models import BandwidthUsageRecord


def date_range(start, stop, step):
    """迭代时间"""
    while start < stop:
        yield start
        start += step


def datetime2str(dt):
    """
    时间列表格式化
    :param dt: list->datetime
    :return: list->str
    """
    date_x_s = []
    for i, d in enumerate(dt):
        formtstr = ""
        if d.month != dt[i-1].month:
            formtstr += "%m/"
        if d.day != dt[i-1].day:
            formtstr += "%d:"
        formtstr += "%H"
        date_x_s.append(d.strftime(formtstr))
    return date_x_s


def brand_usage(account, start, stop, step):
    date_x = list(date_range(start, stop, step))
    data_y_d = []
    data_y_u = []
    for d in date_x:
        bur = BandwidthUsageRecord.objects.filter(
            user=account, add_time__year=d.year, add_time__month=d.month, add_time__day=d.day, add_time__hour=d.hour
        )
        if bur:
            bur = bur[0]
            data_y_d.append(int(bur.bytes_received)/1024)
            data_y_u.append(int(bur.bytes_sent)/1024)
        else:
            data_y_d.append(0)
            data_y_u.append(0)
    line = Line("流量使用情况", width=800)
    date_x_s = datetime2str(date_x)
    line.add("下载", date_x_s, data_y_d, xaxis_rotate=70, yaxis_rotate=0, yaxis_name="bit",
             xaxis_name='year/month/day:hour')
    line.add("上传", date_x_s, data_y_u, xaxis_rotate=70, yaxis_rotate=0, yaxis_name="bit",
             xaxis_name='year/month/day:hour')
    return line


def get_brand_usage_line(account, start, stop, step):
    key = account.account_name+start.strftime('%m-%d-%H-%M')+stop.strftime('%m-%d-%H-%M')+str(step)
    if key in cache:
        line = cache.get(key)
        line = pickle.loads(line)
    else:
        line = brand_usage(account, start, stop, step)
        cache.set(key, pickle.dumps(line), 60*60)
    return line
