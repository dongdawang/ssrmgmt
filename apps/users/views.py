import functools

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import make_password

from goods.models import SsrServer
from .forms import UploadProfilePhoto, ModifyPwdForm
from .models import UserProfile, EmailVerifyRecord, UserModifyRecord
from apps.utils.mixin import LoginRequireMixin
from apps.utils.email_send import send_type_email


class Index(View):

    def get(self, request):
        # session = request.COOKIES.get('sessionid')
        servers = SsrServer.objects.all()
        data = {
            'servers': servers,
        }
        return render(request, 'index.html', data)


class Register(View):
    """用户注册视图
    get:收到request注册请求，返回注册页面
    post:收到request，然后解析其中的注册数据，完成注册，返回注册结果
    """
    def get(self, request):
        return render(request, 'users/register.html', {'result': None})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        user = UserProfile(username=username, email=email)
        user.set_password(password)  # 通过hash和加salt的方式加密
        user.save()  # save操作执行写入数据库的操作，之后才算注册成功

        # 注册之后，判断下是否注册成功
        user = authenticate(username=username, password=password)
        if user is not None:
            return render(request, 'users/register.html', {'result': '注册成功'})
        else:
            return render(request, 'users/register.html', {'result': '注册失败'})


class Login(View):

    def get(self, request):
        return render(request, 'users/login.html', {})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'users/login.html', {'result': '登录失败'})


class Profile(LoginRequireMixin, View):
    def get(self, request):
        user = request.user
        if user is not None:
            return render(request, 'users/profile.html', {})
        else:
            return render(request, 'users/error.html', {'error': '请登录后再操作'})

    def post(self, request):
        pass


def record_modify(modify_type=None):
    """记录每次修改个人信息的装饰器"""
    def decorator(func):
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
            return render(request, "users/profile.html", {})
        else:
            return render(request, "users/error.html", {"error": "form表单无效"})


class SendEmailCode(LoginRequireMixin, View):
    """发送邮箱验证码
    """
    def post(self, request):
        email = request.POST.get('email', '')

        if UserProfile.objects.filter(email=email):
            return render(request, "users/error.html", {"error": "邮箱已存在"})
        else:
            send_type_email(email, send_type="modify_email")
            return render(request, "users/profile.html", {"email_status": "发送成功"})


class ModifyEmail(LoginRequireMixin, View):
    """修改个人邮箱
    """

    @record_modify("modify_email")
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='modify_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return render(request, "users/profile.html", {"email_status": "邮箱修改成功"})
        else:
            return render(request, "users/profile.html", {"email_status": "验证码错误"})

