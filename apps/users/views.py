import functools
import types
import logging
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.db import transaction

from .forms import (UploadProfilePhoto, ModifyPwdForm, ModifyGeneralForm, ModifyUsernameForm, ModifySSRForm,
                    WorkOrderForm)
from .models import UserProfile, UserModifyRecord, SSRAccount, WorkOrder, DataUsageRecord, TradeRecord
from node.models import Node
from apps.utils.mixin import LoginRequireMixin
from apps.utils.email_send import send_type_email, create_code, send_active_email, send_reset_pwd_email
from apps.utils.constants import METHOD_CHOICES, PROTOCOL_CHOICES, OBFS_CHOICES
from apps.utils.nodemgr import NodeStatusCacheMgr
from apps.utils.tools import search_ip_belong

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated




class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        print(self.authentication_classes)
        return Response({'user': 'all'})







class Index(View):

    def get(self, request):
        try:
            user = request.user
            ssr = SSRAccount.objects.get(user=user)
            nscm = NodeStatusCacheMgr()
            nodes = Node.objects.all()
            online_node_count = 0
            for node in nodes:
                if nscm.get_node_status(node.node_id) == 'online':
                    online_node_count += 1

            data = {
                'ssr': ssr,
                'online_node_count': online_node_count,
            }
        except Exception as e:
            logging.error("响应首页请求出错:{}".format(e))
            data = {}
        return render(request, 'backend/index.html', data)


class AuthView(APIView):
    # 如果这个类中的方法不需要认证就能够访问，就直接覆盖配置中的认证类列表
    authentication_classes = []




class System(LoginRequireMixin, View):
    """进入用户中心入口"""
    def get(self, request):
        ssr_all = SSRAccount.objects.all()
        nscm = NodeStatusCacheMgr()
        total = len(ssr_all)
        online_count = 0
        for account in ssr_all:
            if nscm.get_port_ips(account.port):
                online_count += 1
        params = {
            'user': {
                'total': total,
                'online_count': online_count,
                'online_rate': 0 if total == 0 else online_count*100//total
            }
        }
        return render(request, 'backend/system/system.html', params)


class Register(View):
    """用户注册视图
    get:收到request注册请求，返回注册页面
    post:收到request，然后解析其中的注册数据，完成注册，返回注册结果
    """
    def get(self, request):
        return render(request, 'register.html', {'result': None})

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 判断邮箱是否被注册过
        users = UserProfile.objects.filter(email=email)
        if users:
            return render(request, 'register.html', {'result': '邮箱已被注册'})
        else:
            # 发送下邮箱验证码
            res = send_active_email(email)
            if res == "resend":
                return render(request, 'register.html', {'result': '激活邮件已发送，请不要重复注册'})
            elif res == "fail":
                return render(request, 'register.html', {'result': '用户激活邮件发送失败'})
            else:
                # username和email都是unique，所以username必须随机一个避免重复
                user = UserProfile(username=create_code(8), email=email)
                user.set_password(password)  # 通过hash和加salt的方式加密
                user.is_active = False  # 先将用户设为未激活状态
                user.save()  # save操作执行写入数据库的操作，之后才算注册成功

                # 创建一个默认的SSR账号
                ssr = SSRAccount()
                ssr.port = SSRAccount.available_port()
                ssr.passwd = "12345"
                ssr.user = user
                ssr.method = "aes-128-ctr"
                ssr.protocol = "auth_sha1_v4"
                ssr.obfs = "tls1.2_ticket_auth"
                ssr.compatible = True
                ssr.node = Node.default_node()
                ssr.save()
            # 注册之后，判断下是否注册成功
            user = authenticate(username=email, password=password)
            if user is not None:
                return render(request, 'register.html', {'result': '注册成功'})
            else:
                return render(request, 'register.html', {'result': '注册失败'})


class Activate(View):
    """用户激活账号"""
    def get(self, request):
        email = request.GET.get("email")
        code = request.GET.get("code")
        if email in cache:
            verify_code_cache = cache.get(email)
        else:
            verify_code_cache = ""
        if code == verify_code_cache:
            try:
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
            except ObjectDoesNotExist:
                return render(request, 'result.html', {'result': '此邮箱未被注册。'})
            return render(request, 'result.html', {'result': '用户激活成功。'})
        else:
            return render(request, 'result.html', {'result': '此邮箱所对应的验证码不正确。'})


class ResetPwdEmail(View):
    """发送重置密码的邮件"""
    def post(self, request):
        email = request.POST.get('email')
        res = send_reset_pwd_email(email)
        if res == "resend":
            return JsonResponse({'res': '请不要重复发送重置密码的邮件！'})
        elif res == "fail":
            return JsonResponse({'res': '重置密码邮件发送失败！'})
        else:
            return JsonResponse({'res': '重置密码邮件发送成功，请查收！'})


class ResetPwd(View):
    """重置用户密码"""
    def get(self, request):
        email = request.GET.get('email')
        code = request.GET.get('code')
        params = {
            'result': None,
            'email': email,
            'code': code,
        }
        return render(request, 'resetpwd.html', params)

    def post(self, request):
        pwd1 = request.POST.get('password1')
        pwd2 = request.POST.get('password2')
        email = request.POST.get('email')
        code = request.POST.get('code')
        if pwd1 == pwd2:
            key = email + "_resetpwd"
            if key in cache:
                verify_code_cache = cache.get(key)
            else:
                verify_code_cache = ""
            if code == verify_code_cache:
                try:
                    user = UserProfile.objects.get(email=email)
                    user.set_password(pwd1)
                    user.save()
                except ObjectDoesNotExist:
                    return render(request, 'resetpwd.html', {'result': '此邮箱未被注册。'})
                return render(request, 'resetpwd.html', {'result': '用户密码重置成功。'})
            else:
                return render(request, 'resetpwd.html', {'result': '此邮箱所对应的验证码不正确。'})
        else:
            return render(request, 'resetpwd.html', {'result': '两次输入的密码不一样'})


class Login(View):

    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'login.html', {'result': '用户未激活'})
        else:
            return render(request, 'login.html', {'result': '登录失败'})


def record_modify(modify_type=None):
    """记录每次修改个人信息的装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            modify = UserModifyRecord()
            modify.user = request.user
            modify.modify_type = modify_type
            result = func(self, request, *args, **kwargs)
            # 需要修改操作完成之后才将修改记录保存
            modify.save()
            return result
        return wrapper
    return decorator


class Profile(LoginRequireMixin, View):
    def get(self, request):
        user = request.user
        if user is not None:
            return render(request, 'backend/my/profile.html', {})
        else:
            return render(request, 'backend/my/profile.html', {"error": '请登录后再操作'})

    def post(self, request):
        pass


class AccountEdit(LoginRequireMixin, View):
    """返回用户数据编辑页面"""
    def get(self, request):
        user = request.user
        constants = {
            "METHODS": [method[0] for method in METHOD_CHOICES],
            "PROTOCOLS": [protocol[0] for protocol in PROTOCOL_CHOICES],
            "OBFSS": [obfs[0] for obfs in OBFS_CHOICES],
            "ssr": SSRAccount.objects.get(user=user)
        }
        if user is not None:
            return render(request, 'backend/my/account_edit.html', constants)
        else:
            return render(request, '/')


class AccountProfilePhotoModify(LoginRequireMixin, View):
    """用户修改头像"""
    @record_modify("modify_profile_photo")
    def post(self, request):
        profile_photo_form = UploadProfilePhoto(request.POST, request.FILES, instance=request.user)
        if profile_photo_form.is_valid():
            profile_photo_form.save()
            return JsonResponse({"res": "修改头像成功"})
        else:
            return JsonResponse({"res": "修改头像失败，表单非法"})


class AccountPwdModify(LoginRequireMixin, View):
    """修改用户密码"""

    @record_modify("modify_password")
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        # form表单中定义了，必须是符合form表单的才算是有效表单，比如密码长度要大于5
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return JsonResponse({"res": "两个密码不一样"})
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return JsonResponse({"res": "密码修改成功！"})
        else:
            return JsonResponse({"res": "form表单无效"})


class AccountGeneralModify(LoginRequireMixin, View):
    """修改用户一般信息"""
    def post(self, request):
        general_form = ModifyGeneralForm(request.POST)
        if general_form.is_valid():
            gender = request.POST.get('gender')
            birthday = request.POST.get('birthday')
            address = request.POST.get('address')
            mobile = request.POST.get('mobile')
            user = request.user
            user.gender = gender
            user.birthday = birthday
            user.address = address
            user.mobile = mobile
            user.save()
            return JsonResponse({"res": "修改成功"})
        else:
            return JsonResponse({"res": "修改失败"})


class AccountNameModify(LoginRequireMixin, View):
    """修改用户的username"""
    def post(self, request):
        username_form = ModifyUsernameForm(request.POST)
        if username_form.is_valid():
            username = request.POST.get('username')
            if UserProfile.objects.filter(username=username):
                return JsonResponse({"res": "用户名已存在，修改失败！"})
            user = request.user
            user.username = username
            user.save()
            return JsonResponse({"res": "用户名修改成功"})
        else:
            return JsonResponse({"res": "表单非法，请检查输入是否合法！"})


class AccountSSRModify(LoginRequireMixin, View):
    """修改用户的SSR"""
    def post(self, request):
        ssr_form = ModifySSRForm(request.POST)
        if ssr_form.is_valid():
            passwd = request.POST.get('passwd')
            method = request.POST.get('method')
            protocol = request.POST.get('protocol')
            obfs = request.POST.get('obfs')
            compatible = request.POST.get('compatible')
            if compatible == "true":
                compatible = True
            else:
                compatible = False
            user = request.user
            ssr = SSRAccount.objects.get(user=user)
            ssr.passwd = passwd
            ssr.method = method
            ssr.protocol = protocol
            ssr.obfs = obfs
            ssr.compatible = compatible
            ssr.save()
            return JsonResponse({"res": "SSR配置修改成功"})
        else:
            return JsonResponse({"res": "SSR配置修改失败，表单非法"})


class AccountEmailModify(LoginRequireMixin, View):
    """修改用户邮箱"""
    def post(self, request):
        email = request.POST.get('email')
        verify_code = request.POST.get('verify_code')
        if email in cache:
            verify_code_cache = cache.get(email)
        else:
            verify_code_cache = ""
        if verify_code == verify_code_cache:
            # username和email都是unique，所以username必须随机一个避免重复
            user = request.user
            user.email = email
            user.save()  # save操作执行写入数据库的操作，之后才算注册成功
            return JsonResponse({"res": "邮箱修改成功"})
        else:
            return JsonResponse({"res": "邮箱修改失败, 验证码不正确"})


class ProfileShow(LoginRequireMixin, View):
    """显示用户属性"""
    def get(self, request):
        user = request.user
        params = {
            'level': user.user_level(),
        }
        return render(request, 'backend/my/profile.html', params)


class ProfileCenter(LoginRequireMixin, View):
    """显示用户中心"""
    def get(self, request):
        user = request.user
        ssr_account = SSRAccount.objects.get(user=user)
        nscm = NodeStatusCacheMgr()
        ip_info = {}
        ips = nscm.get_port_ips(ssr_account.port)
        # 查询ip归属地
        for ip in ips:
            ip_info.setdefault(ip, search_ip_belong(ip))

        usages = DataUsageRecord.last_30_days(ssr_account)
        params = {
            'ssr_account': ssr_account,
            'usages': usages,
            'ip_info': ip_info
        }
        return render(request, 'backend/my/center.html', params)


class WorkOrderShow(LoginRequireMixin, View):
    """工单处理"""
    def get(self, request):
        user = request.user
        workorder = WorkOrder.objects.filter(user=user)
        params = {
            "workorder": workorder
        }
        return render(request, 'backend/my/workorder.html', params)


class WorkorderView(LoginRequireMixin, View):
    """显示详细工单"""
    def get(self, request, wo_id):
        wo = WorkOrder.objects.get(id=wo_id)
        return render(request, 'backend/my/workorder_view.html', {'workorder': wo})


class WorkorderDelete(LoginRequireMixin, View):
    """删除工单"""
    def get(self, request, wo_id):
        try:
            wo = WorkOrder.objects.get(id=wo_id)
            wo.delete()
            return JsonResponse({"res": "删除工单成功"})
        except Exception as e:
            return JsonResponse({"res": "删除工单失败"})


class WorkOrderAdd(LoginRequireMixin, View):
    """工单"""
    def get(self, request):
        user = request.user
        return render(request, 'backend/my/workorder_add.html')

    def post(self, request):
        workorder = WorkOrderForm(request.POST)
        if workorder.is_valid():
            wo = WorkOrder()
            wo.user = request.user
            wo.title = request.POST.get('title')
            wo.body = request.POST.get('body')
            wo.save()
            return JsonResponse({"res": "工单提交成功"})
        else:
            return JsonResponse({"res": "表单不合法"})


# @method_decorator(transaction.atomic, name='post')
class BuyTime(LoginRequireMixin, View):
    """购买时长"""
    def get(self, request):
        user = request.user
        ssr = SSRAccount.objects.get(user=user)
        params = {
            'coin_nums': user.coin_nums,
            'ssr': ssr,
        }
        return render(request, 'backend/buy/time.html', params)

    @method_decorator(transaction.atomic)
    def post(self, request):
        """数据库原子性：
        关于保证增加(1)ssr时长和(2)减去用户硬币数这个两个操作的事务原子性

        django的ORM在对数据库操作时，在一个view上设置transaction.atomic，
        则view中所有的ORM操作都会在view结束时自动commit。所以就可以保证在一
        个view中出现的数据库操作具有原子性atomic。
        """
        user = request.user
        try:
            ssr = SSRAccount.objects.get(user=user)
            day = request.POST.get('day')
            if int(day) > user.coin_nums:
                return JsonResponse({"res": "硬币余额不足！"})
            if ssr.expiration_time < datetime.now():
                ssr.expiration_time = datetime.now() + timedelta(days=int(day))
            else:
                ssr.expiration_time += timedelta(days=int(day))
            user.coin_nums -= int(day)
            trade = TradeRecord()
            trade.user = user
            trade.amount = int(day)
            trade.time = int(day)
            user.save()
            ssr.save()
            trade.save()
        except ObjectDoesNotExist as ex:
            logging.error("购买时长出错:{}".format(ex))
            return JsonResponse({"res": "购买时长出错！"})

        return JsonResponse({
            "res": "购买成功, \n当前SSR到期时间:{}".format(ssr.expiration_time.strftime('%Y-%m-%d %H:%M:%S'))
        })


class TradeRecodeShow(LoginRequireMixin, View):
    """显示用户交易记录"""
    def get(self, request):
        user = request.user
        trades = TradeRecord.objects.filter(user=user)
        params = {
            "trades": trades
        }
        return render(request, 'backend/buy/records.html', params)


class SendEmailCode(View):
    """发送邮箱验证码
    """
    def post(self, request):
        email = request.POST.get('email', '')
        email_type = request.POST.get('email_type', '')

        if UserProfile.objects.filter(email=email):
            return JsonResponse({'res': 'already_existed'})
        else:
            result = send_type_email(email, send_type=email_type)
            if result == "email_send_ok":
                return JsonResponse({'res': 'success'})
            elif result == "email_resend":
                return JsonResponse({'res': 'resend'})
            elif result == "email_send_fail":
                return JsonResponse({'res': 'fail'})
            else:
                return JsonResponse({'res': 'unknown'})


class Tutorial(LoginRequireMixin, View):
    """显示使用教程"""
    def get(self, request):
        return render(request, 'backend/usage/tutorial.html', {})
