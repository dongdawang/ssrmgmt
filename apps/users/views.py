import functools
import types
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from goods.models import SsrServer, SsrAccount
from .forms import UploadProfilePhoto, ModifyPwdForm
from .models import UserProfile, EmailVerifyRecord, UserModifyRecord
from apps.utils.mixin import LoginRequireMixin
from apps.utils.email_send import send_type_email, create_code

from pyecharts import Bar
from apps.utils.nets import get_host_ip_cache
from apps.utils.charts import brand_usage, get_brand_usage_line


class Index(View):

    def get(self, request):
        servers = SsrServer.objects.all()
        data = {
            'servers': servers,
            'ip': get_host_ip_cache(),
        }
        return render(request, 'backend/system/system.html', data)


class Register(View):
    """用户注册视图
    get:收到request注册请求，返回注册页面
    post:收到request，然后解析其中的注册数据，完成注册，返回注册结果
    """
    def get(self, request):
        return render(request, 'register.html', {'result': None})

    def post(self, request):
        email = request.POST.get('email')
        verify_code = request.POST.get('verify_code')
        password = request.POST.get('password')

        if email in cache:
            verify_code_cache = cache.get(email)
        else:
            verify_code_cache = ""
        if verify_code == verify_code_cache:
            # username和email都是unique，所以username必须随机一个避免重复
            user = UserProfile(username=create_code(8), email=email)
            user.set_password(password)  # 通过hash和加salt的方式加密
            user.save()  # save操作执行写入数据库的操作，之后才算注册成功

            # 注册之后，判断下是否注册成功
            user = authenticate(username=email, password=password)
            if user is not None:
                return render(request, 'register.html', {'result': '注册成功'})
            else:
                return render(request, 'register.html', {'result': '注册失败'})
        else:
            return render(request, 'register.html', {'result': '注册失败，验证码不正确！'})


class Login(View):

    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'result': '登录失败'})


class Profile(LoginRequireMixin, View):
    def get(self, request):
        user = request.user
        if user is not None:
            return render(request, 'backend/my/profile.html', {})
        else:
            return render(request, 'backend/my/profile.html', {"error": '请登录后再操作'})

    def post(self, request):
        pass


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


class ProfilePhotoUpload(LoginRequireMixin, View):
    """用户修改头像
    """
    @record_modify("modify_profile_photo")
    def post(self, request):
        profile_photo_form = UploadProfilePhoto(request.POST, request.FILES, instance=request.user)
        if profile_photo_form.is_valid():
            profile_photo_form.save()
        return render(request, 'users/profile.html', {})


class ModifyPwd(LoginRequireMixin, View):
    """个人中心修改密码
    """
    def get(self, request):
        if request.user is not None:
            return render(request, 'users/password.html', {})
        else:
            return render(request, 'users/error.html', {"error": '请登录后再操作'})

    @record_modify("modify_password")
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        # form表单中定义了，必须是符合form表单的才算是有效表单，比如密码长度要大于5
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return render(request, "users/error.html", {"error": "两个密码不一样"})
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return render(request, "users/profile.html", {"status": "密码修改成功！"})
        else:
            return render(request, "users/error.html", {"error": "form表单无效"})


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


class ModifyEmail(LoginRequireMixin, View):
    """修改个人邮箱
    """
    def get(self, request):
        user = request.user
        if user is not None:
            dct = {}
            return render(request, 'users/email.html', dct)
        else:
            return render(request, 'users/error.html', {"error": '请登录后再操作'})

    @record_modify("modify_email")
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='modify_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return render(request, "users/profile.html", {"status": "邮箱修改成功"})
        else:
            return render(request, "users/email.html", {"status": "验证码错误"})


class UserCharts(LoginRequireMixin, View):
    """管理用户的图表
    """
    def get(self, request):
        user = request.user
        accounts = SsrAccount.objects.filter(user=user)
        times = ['最近一天', '最近一周', '最近一个月']
        dct = {
            'accounts': accounts,
            'times': times
        }
        return render(request, 'users/charts.html', dct)

    def post(self, request):
        user = request.user
        accounts = SsrAccount.objects.filter(user=user)
        times = ['最近一天', '最近一周', '最近一个月']
        account_name = request.POST.get('account')
        account = SsrAccount.objects.filter(account_name=account_name)
        if account:
            account = account[0]
        time = request.POST.get('time')
        line = bar()
        # 定制图表
        if time == '最近一天':
            now = datetime.now()
            # now = datetime(2018, 8, 17, 0)
            start = now - timedelta(days=1)
            stop = now
            step = timedelta(hours=1)
            line = get_brand_usage_line(account, start, stop, step)
        dct = {
            'accounts': accounts,
            'times': times,
            "myechart": line.render_embed(),
            "host": "https://pyecharts.github.io/assets/js",
            "script_list": line.get_js_dependencies(),
            "error": '请登录后再操作',
        }
        return render(request, 'users/charts.html', dct)


class ModifyShow(LoginRequireMixin, View):
    """显示用户的修改记录"""
    def get(self, request):
        user = request.user
        modifies = UserModifyRecord.objects.filter(user=user)
        return render(request, 'users/modify.html', {'modifies': modifies})

    def post(self, request):
        pass


class UserAccounts(LoginRequireMixin, View):
    """获取用户创建的SSR账号
    """
    def get(self, request):
        user = request.user
        accounts = SsrAccount.objects.filter(user=user)
        return render(request, 'users/accounts.html', {'accounts': accounts})


def bar():
    bar_ins = Bar("未成功生成图表", "ERROR")
    bar_ins.add("元素", [], [], is_more_utils=False)
    return bar_ins
