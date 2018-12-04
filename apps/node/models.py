from datetime import datetime, timedelta

from django.db import models


class Node(models.Model):
    # 节点ID唯一
    node_id = models.IntegerField(verbose_name="节点id", null=False, blank=False, unique=True)
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="节点名称")
    ip = models.GenericIPAddressField(verbose_name="节点ip")

    @classmethod
    def default_node(cls):
        """获取一个默认的节点"""
        node = cls.objects.first()
        if not node:
            n = Node(node_id=1, name="默认节点", ip="0.0.0.0")
            n.save()
            return n
        else:
            return node


class DataUsageRecord(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, verbose_name="节点")
    bytes_recv = models.CharField(max_length=20, null=False, blank=False, verbose_name="收到的数据")
    bytes_sent = models.CharField(max_length=20, null=False, blank=False, verbose_name="发送的数据")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户流量使用情况"
        verbose_name_plural = verbose_name

    @classmethod
    def last_30_days(cls, node):
        """最近一个月的流量使用情况，粒度为1天"""
        now = datetime.now()
        step = timedelta(days=1)
        start = now - timedelta(days=30)
        data_x = cls.date_range(start, now, step)
        usages = []
        for d in data_x:
            data_usage = cls.objects.filter(node=node, add_time__year=d.year, add_time__month=d.month,
                                            add_time__day=d.day)
            yu = data_usage[0].bytes_sent if data_usage else 0
            yd = data_usage[0].bytes_recv if data_usage else 0
            usage = {
                "x": d,
                "yu": int(yu) // 1024**2,
                "yd": int(yd) // 1024**2,
            }
            usages.append(usage)

        return usages

    @staticmethod
    def date_range(start, stop, step):
        """迭代时间"""
        while start < stop:
            yield start
            start += step

