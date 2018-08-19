from __future__ import absolute_import, unicode_literals

# from celery import shared_task
from celery.task import task
from .models import BandwidthUsageRecord, UserProfile
# from apps.goods.models import SsrAccount 这样不行
from goods.models import SsrAccount
from apps.utils.ssrmgr import SsrMgr


@task
def band_record():
    srg = SsrMgr()
    band_usage = srg.band_record()
    # 遍历user信息
    for name, band in band_usage.items():
        account = SsrAccount.objects.filter(account_name=name)
        if account is not None:
            bur = BandwidthUsageRecord()
            if bur:
                bur.user = account[0]
                bur.bytes_received = band['download']
                bur.bytes_sent = band['upload']
                bur.save()
    # 获取user的流量信息后，将其流量清空
    srg.clear_band()
    return "OK Record"


@task
def generate_random_band():
    """给每个用户生成一个随机的流量，测试使用"""
    srg = SsrMgr()
    srg.random_band()
