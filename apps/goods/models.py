from datetime import datetime

from django.db import models

from users.models import UserProfile


class SsrAccount(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    account_name = models.CharField(max_length=30, verbose_name="SSR账户名")
    ip = models.GenericIPAddressField(max_length=15, verbose_name="服务器IP")
    port = models.CharField(max_length=10, verbose_name="账户端口")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "SSR账户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.account_name


class SsrServer(models.Model):
    name = models.CharField(max_length=30, null=False, verbose_name="服务器名称")
    address = models.CharField(max_length=30, null=False, verbose_name="服务器归属地")
    ip = models.GenericIPAddressField(max_length=15, null=False, verbose_name="服务器IP")
    Weights = models.IntegerField(default=100, null=False, verbose_name="服务权重")
    is_enable = models.BooleanField(default=False, null=False, verbose_name="服务器是否启用")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "SSR服务器"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

