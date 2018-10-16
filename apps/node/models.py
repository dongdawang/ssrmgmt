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
