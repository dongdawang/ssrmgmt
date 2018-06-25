from django.shortcuts import render, HttpResponse
from django.views import View


class Ping(View):
    """定义ping命令的视图函数，由于浏览器不能构建原始报文和操作设备IO
    所以只能借用http报文来测试延迟
    """
    def get(self, request):
        return HttpResponse('')

