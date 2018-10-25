import json

from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core import cache

from users.models import UserProfile, SSRAccount, DataUsageRecord


@method_decorator(csrf_exempt, name="dispatch")
class User(View):
    """SSR服务器用户相关的API"""

    def get(self, request):
        node_id = request.GET.get("node_id")
        ssrs = SSRAccount.objects.filter(node__node_id=node_id)
        # users = UserProfile.objects.all()
        user_json = {
            'ssrs': []
        }
        for ssr in ssrs:
            user_json['ssrs'].append(
                {
                    "user": ssr.user.email,
                    "port": ssr.port,
                    "passwd": ssr.passwd,
                    "method": ssr.method,
                    "protocol": ssr.protocol,
                    "obfs": ssr.obfs,
                    "expiration_time": ssr.expiration_time,
                    "node_id": node_id,
                }
            )
        return JsonResponse(user_json)

    def post(self, request):
        node_id = request.GET.get("node_id")
        ssrs = SSRAccount.objects.filter(node__node_id=node_id)
        # users = UserProfile.objects.all()
        user_json = {
            'ssrs': []
        }
        for ssr in ssrs:
            user_json['ssrs'].append(
                {
                    "user": ssr.user.email,
                    "port": ssr.port,
                    "passwd": ssr.passwd,
                    "method": ssr.method,
                    "protocol": ssr.protocol,
                    "obfs": ssr.obfs,
                    "expiration_time": ssr.expiration_time,
                    "node_id": node_id,
                }
            )
        return JsonResponse(user_json)


@method_decorator(csrf_exempt, name="dispatch")
class NodeAlive(View):
    """更新节点是否在线"""
    def post(self, request):
        pass


@method_decorator(csrf_exempt, name="dispatch")
class Transfer(View):
    """存储用户流量信息"""
    def post(self, request):
        datas = json.loads(request.body.decode("utf-8"))
        datas = datas['datas']
        try:
            for data in datas:
                port = data['port']
                ssr = SSRAccount.objects.filter(port=port)
                if ssr:
                    ssr = ssr[0]
                    data_usage = DataUsageRecord()
                    data_usage.ssr = ssr
                    data_usage.bytes_sent = data['u']
                    data_usage.bytes_received = data['d']
                    data_usage.save()
        except Exception as e:
            return JsonResponse({'res': 'fail'})
        return JsonResponse({'res': 'ok'})
