from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    gender_choices = (
        ('male', '男'),
        ('female', '女'),
    )
    nick_name = models.CharField(max_length=20, default="", verbose_name="昵称")
    birthday = models.DateField(blank=True, null=True, verbose_name="生日")
    gender = models.CharField(max_length=6, choices=gender_choices, default='male', verbose_name="性别")
    address = models.CharField(max_length=100, default="", verbose_name="地址")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号")
    profile_photo = models.ImageField(
        max_length=100, upload_to='image/%Y/%m',  default='image/default.png', verbose_name="用户头像")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=10, verbose_name="验证码")
    email = models.EmailField(max_length=30, verbose_name="邮箱")
    type_choices = (
        ('register', '注册'),
        ('forget', '找回密码'),
        ('modify_email', '修改邮箱'),
    )
    send_type = models.CharField(max_length=30, choices=type_choices, verbose_name="验证码类型")
    send_time = models.DateTimeField(default=datetime.now, verbose_name="发送时间")

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name


class BandwidthUsageRecord(models.Model):
    """记录用户在各个时间点的流量使用情况
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    bytes_received = models.CharField(max_length=20, null=False, blank=False, verbose_name="收到的数据")
    bytes_sent = models.CharField(max_length=20, null=False, blank=False, verbose_name="发送的数据")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户流量使用情况"
        verbose_name_plural = verbose_name


class UserModifyRecord(models.Model):
    """记录账号信息修改的记录
    """
    chics = (
        ("modify_email", "修改邮箱"),
        ("modify_password", "修改密码"),
        ("modify_profile_photo", "修改头像"),
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    modify_type = models.CharField(choices=chics, max_length=25, verbose_name="修改类型")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "账号修改记录"
        verbose_name_plural = verbose_name
