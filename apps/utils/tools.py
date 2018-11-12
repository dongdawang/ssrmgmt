import urllib
import urllib.request
import json
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


def search_ip_belong(ip):
    taobao_api = "http://ip.taobao.com/service/getIpInfo.php?ip="
    headers = ('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    respon = opener.open(taobao_api + ip).read()
    respon = respon.decode('UTF-8')
    res = json.loads(respon)
    if res['code'] == 0:
        data = res['data']
        belong_to = data['country'] + data['area'] + data['region'] + data['city'] + data['isp']
    else:
        belong_to = ""
    return belong_to
