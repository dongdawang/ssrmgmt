from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

import markdown
from apps.utils.constants import METHOD_CHOICES, PROTOCOL_CHOICES, OBFS_CHOICES
from node.models import Node


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
        for k, v in levels.items():
            if v[0] <= self.experience < v[1]:
                return k
        return 0


class SSRAccount(models.Model):
    expiration_time = models.DateTimeField(verbose_name='SSR有效期', default=timezone.now)
    port = models.PositiveIntegerField(verbose_name="用户端口", unique=True)
    passwd = models.CharField(max_length=30, null=True, blank=True)
    method = models.CharField(verbose_name="加密方法", max_length=30, choices=METHOD_CHOICES,
                              default='none')
    protocol = models.CharField(verbose_name="协议", max_length=30, choices=PROTOCOL_CHOICES,
                                default='origin')
    obfs = models.CharField(verbose_name="混淆方法", max_length=30, choices=OBFS_CHOICES,
                            default='plain')
    obfs_enable = models.BooleanField(verbose_name="是否启用混淆", default=False)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, verbose_name="关联的节点")
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, verbose_name="所有用户")

    @classmethod
    def available_port(cls):
        """返回一个可用的端口"""
        exist_port = cls.objects.values_list('port')
        ports = [port for port in range(7000, 8000)]
        return list(set(ports).difference(set(exist_port)))[0]

    def __str__(self):
        return type(self.port)


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


class WorkOrder(models.Model):
    """工单"""
    stats = {
        ('open', 'open'),
        ('closed', 'closed')
    }
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=50, verbose_name="标题")
    body = models.TextField(verbose_name="工单内容")
    status = models.CharField(max_length=20, default="open", choices=stats, verbose_name="工单状态")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "工单"
        verbose_name_plural = verbose_name


class DataUsageRecord(models.Model):
    """记录用户在各个时间点的流量使用情况"""
    # model循环导入问题
    # user = models.ForeignKey("goods.SsrAccount", on_delete=models.CASCADE, verbose_name="用户")
    ssr = models.ForeignKey(SSRAccount, on_delete=models.CASCADE, verbose_name="SSR账户")
    bytes_received = models.CharField(max_length=20, null=False, blank=False, verbose_name="收到的数据")
    bytes_sent = models.CharField(max_length=20, null=False, blank=False, verbose_name="发送的数据")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户流量使用情况"
        verbose_name_plural = verbose_name

    def last_week(self):
        pass

    @classmethod
    def last_30_days(cls, ssr):
        """最近一个月的流量使用情况，粒度为1天"""
        now = datetime.now()
        step = timedelta(days=1)
        start = now - timedelta(days=30)
        data_x = cls.date_range(start, now, step)
        usages = []
        for d in data_x:
            data_usage = cls.objects.filter(ssr=ssr, add_time__year=d.year, add_time__month=d.month,
                                            add_time__day=d.day)
            yu = data_usage[0].bytes_sent if data_usage else 0
            yd = data_usage[0].bytes_received if data_usage else 0
            usage = {
                "x": d,
                "yu": int(yu)/1024,
                "yd": int(yd)/1024,
            }
            usages.append(usage)

        return usages

    @staticmethod
    def date_range(start, stop, step):
        """迭代时间"""
        while start < stop:
            yield start
            start += step


class TradeRecord(models.Model):
    """ 交易明细"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户")
    amount = models.DecimalField('交易金额', max_digits=19, decimal_places=4)
    time = models.PositiveIntegerField(verbose_name="购买天数")
    add_time = models.DateTimeField(verbose_name='交易时间', default=datetime.now)
