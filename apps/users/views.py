import functools
import types
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from .forms import (UploadProfilePhoto, ModifyPwdForm, ModifyGeneralForm, ModifyUsernameForm, ModifySSRForm,
                    WorkOrderForm)
from .models import UserProfile, UserModifyRecord, SSRAccount, WorkOrder
from node.models import Node
from apps.utils.mixin import LoginRequireMixin
from apps.utils.email_send import send_type_email, create_code

from apps.utils.nets import get_host_ip_cache
from apps.utils.constants import METHOD_CHOICES, PROTOCOL_CHOICES, OBFS_CHOICES
from apps.utils.ssrmgr import SS, SSR


class Index(View):

    def get(self, request):
        data = {
            'servers': "",
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

            # 创建一个默认的SSR账号
            ssr = SSRAccount()
            ssr.port = SSRAccount.available_port()
            ssr.passwd = "12345"
            ssr.user = user
            ssr.node = Node.default_node()
            ssr.save()

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
            obfs_enable = request.POST.get('obfs_enable')
            if obfs_enable == "true":
                obfs_enable = True
            else:
                obfs_enable = False
            user = request.user
            ssr = SSRAccount.objects.get(user=user)
            ssr.passwd = passwd
            ssr.method = method
            ssr.protocol = protocol
            ssr.obfs = obfs
            ssr.obfs_enable = obfs_enable
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
        params = {
            'ssr_account': ssr_account,
            'ss': SS(ssr_account),
            'ssr': SSR(ssr_account)
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
                return JsonResponse({"res": "两个密码不一样"})
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return JsonResponse({"res": "密码修改成功！"})
        else:
            return JsonResponse({"res": "form表单无效"})


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


class UserCharts(LoginRequireMixin, View):
    """管理用户的图表
    """
    def get(self, request):
        user = request.user
        times = ['最近一天', '最近一周', '最近一个月']
        dct = {
            'accounts': "",
            'times': times
        }
        return render(request, 'users/charts.html', dct)

    def post(self, request):
        # user = request.user
        # times = ['最近一天', '最近一周', '最近一个月']
        # account_name = request.POST.get('account')
        # if account:
        #     account = account[0]
        # time = request.POST.get('time')
        # line = bar()
        # # 定制图表
        # if time == '最近一天':
        #     now = datetime.now()
        #     # now = datetime(2018, 8, 17, 0)
        #     start = now - timedelta(days=1)
        #     stop = now
        #     step = timedelta(hours=1)
        #     line = get_brand_usage_line(account, start, stop, step)
        # dct = {
        #     'accounts': accounts,
        #     'times': times,
        #     "myechart": line.render_embed(),
        #     "host": "https://pyecharts.github.io/assets/js",
        #     "script_list": line.get_js_dependencies(),
        #     "error": '请登录后再操作',
        # }
        return render(request, 'users/charts.html', {})


class ModifyShow(LoginRequireMixin, View):
    """显示用户的修改记录"""
    def get(self, request):
        user = request.user
        modifies = UserModifyRecord.objects.filter(user=user)
        return render(request, 'users/modify.html', {'modifies': modifies})

    def post(self, request):
        pass

