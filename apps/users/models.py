from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
# from goods.models import SsrAccount

import markdown


class UserProfile(AbstractUser):
    gender_choices = (
        ('male', '男'),
        ('female', '女'),
    )
    # 重写下email字段，保证email不能重复，支持email登录
    email = models.EmailField(_('email address'), unique=True)
    nick_name = models.CharField(max_length=20, default="", verbose_name="昵称")
    birthday = models.DateField(blank=True, null=True, verbose_name="生日")
    gender = models.CharField(max_length=6, choices=gender_choices, default='male', verbose_name="性别")
    address = models.CharField(max_length=100, default="", verbose_name="地址")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号")
    profile_photo = models.ImageField(
        max_length=100, upload_to='image/%Y/%m',  default='image/default.png', verbose_name="用户头像")

    # 业务相关属性
    coin_nums = models.DecimalField(verbose_name="硬币数", decimal_places=2, max_digits=10,
                                    default=10, editable=True, null=True, blank=True)
    experience = models.PositiveIntegerField(verbose_name="经验", default=0, help_text="用于计算用户等级",
                                             validators=[MaxValueValidator(100), MinValueValidator(0)])

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    @classmethod
    def user_count(cls):
        """用户总数计算"""
        return len(cls.objects.all())

    def user_level(self):
        """获取用户的等级"""
        # 等级区间
        levels = {
            0: [0, 10],
            1: [10, 50],
            2: [50, 200],
            3: [200, 500],
            4: [500, 1000],
            5: [1000, float('inf')]
        }
        for k, v in levels:
            if v[0] <= self.experience < v[1]:
                return k
        return 0


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
    # model循环导入问题
    user = models.ForeignKey("goods.SsrAccount", on_delete=models.CASCADE, verbose_name="用户")
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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="账号")
    modify_type = models.CharField(choices=chics, max_length=25, verbose_name="修改类型")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "账号修改记录"
        verbose_name_plural = verbose_name


class Announcement(models.Model):
    """公告界面"""
    time = models.DateTimeField('时间', auto_now_add=True)
    body = models.TextField('主体')

    def __str__(self):
        return '日期:{}'.format(str(self.time)[:9])

    # 重写save函数，将文本渲染成markdown格式存入数据库
    def save(self, *args, **kwargs):
        # 首先实例化一个MarkDown类，来渲染一下body的文本 成为html文本
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
        ])
        self.body = md.convert(self.body)
        # 调动父类save 将数据保存到数据库中
        super(Announcement, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = '系统公告'
        ordering = ('-time', )
