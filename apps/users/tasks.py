from __future__ import absolute_import, unicode_literals

# from celery import shared_task
from celery.task import task
from .models import BandwidthUsageRecord, UserProfile


@task
def model_record():
    # tr = TaskRecord()
    # tr.save()
    return "x111111111"


@task
def band_record():
    user = UserProfile.objects.all()[0]
    bur = BandwidthUsageRecord()
    bur.user = user
    bur.bytes_received = "100k"
    bur.bytes_sent = "10k"
    bur.save()
    return "OK Record"
