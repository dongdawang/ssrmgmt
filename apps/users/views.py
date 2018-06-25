from django.shortcuts import render, render_to_response, redirect
from django.views import View
from django.contrib.auth import authenticate

from goods.models import SsrServer


def judge():
    user = authenticate(user='one', password='secret')
    if user is not None:
        pass  # 登录成功
    else:
        pass  # 登录失败


class Index(View):

    def get(self, request):
        session = request.COOKIES.get('sessionid')
        servers = SsrServer.objects.all()
        data = {
            'servers': servers
        }
        return render_to_response('index.html', data)


class Login(View):

    def get(self, request):
        return render(request, 'users/login.html', {})

    def post(self, request):
        return redirect('/')
