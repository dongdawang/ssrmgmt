from __future__ import absolute_import, unicode_literals

# from celery import shared_task
from celery.task import task
from .models import BandwidthUsageRecord, UserProfile
# from apps.goods.models import SsrAccount 这样不行
from goods.models import SsrAccount
from apps.utils.ssrmgr import SsrMgr


@task
def model_record():
    # tr = TaskRecord()
    # tr.save()
    return "x111111111"


@task
def band_record():
    srg = SsrMgr()
    band_usage = srg.band_record()
    # 遍历user信息
    for name, band in band_usage.items():
        account = SsrAccount.objects.filter(account_name=name)
        if account is not None:
            bur = BandwidthUsageRecord()
            bur.user = account[0]
            bur.bytes_received = band['download']
            bur.bytes_sent = band['upload']
            bur.save()
    return "OK Record"
