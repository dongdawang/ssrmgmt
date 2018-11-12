import json
import logging

from django.views import View
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from users.models import UserProfile, SSRAccount, DataUsageRecord
from node import models
from apps.utils.mixin import VerifyAPITokenMixin
from apps.utils.nodemgr import NodeStatusCacheMgr

import jwt


@method_decorator(csrf_exempt, name="dispatch")
class User(VerifyAPITokenMixin, View):
    """
    SSR服务器用户相关的API
    """
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
                    "protocol": ssr.protocol+"_compatible" if ssr.compatible else ssr.protocol,
                    "obfs": ssr.obfs+"_compatible" if ssr.compatible else ssr.obfs,
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
                    "protocol": ssr.protocol+"_compatible" if ssr.compatible else ssr.protocol,
                    "obfs": ssr.obfs+"_compatible" if ssr.compatible else ssr.obfs,
                    "expiration_time": ssr.expiration_time,
                    "node_id": node_id,
                }
            )
        return JsonResponse(user_json)


@method_decorator(csrf_exempt, name="dispatch")
class NodeStatus(VerifyAPITokenMixin, View):
    """
    更新节点状态
    """
    def post(self, request):
        try:
            stat = json.loads(request.body.decode("utf-8"))
            node_id = stat['node_id']
            node_status = stat['is_online']
            port_status = stat['port']

            nscm = NodeStatusCacheMgr()
            nscm.set_node_status(node_id, node_status)

            for port, ips in port_status.items():
                nscm.set_port_ips(port, ips)

            return HttpResponse('OK', status=200)
        except KeyError as e:
            return HttpResponse('Internal Server Error', status=500)


@method_decorator(csrf_exempt, name="dispatch")
class UserTransfer(VerifyAPITokenMixin, View):
    """
    存储用户流量信息
    """
    def post(self, request):
        usage = json.loads(request.body.decode("utf-8"))
        try:
            for port, data in usage.items():
                port = int(port)
                ssr = SSRAccount.objects.filter(port=port)
                if ssr:
                    ssr = ssr[0]
                    data_usage = DataUsageRecord()
                    data_usage.ssr = ssr
                    data_usage.bytes_sent = data['u']
                    data_usage.bytes_received = data['d']
                    data_usage.save()
        except Exception as e:
            return HttpResponse('Internal Server Error', status=500)
        return HttpResponse('OK', status=200)


@method_decorator(csrf_exempt, name="dispatch")
class NodeTransfer(VerifyAPITokenMixin, View):
    """
    存储主机流量
    """
    def post(self, request):
        usage = json.loads(request.body.decode("utf-8"))
        try:
            for node_id, data in usage.items():
                node_id = str(node_id)
                node = models.Node.objects.filter(node_id=node_id)
                if node:
                    node = node[0]
                    data_usage = models.DataUsageRecord()
                    data_usage.node = node
                    data_usage.bytes_sent = data['sent']
                    data_usage.bytes_recv = data['recv']
                    data_usage.save()
                    return HttpResponse('OK', status=200)
                else:
                    return JsonResponse('Not Implemented', status=501)
        except Exception as e:
            return HttpResponse('Internal Server Error', status=500)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateToken(View):
    """生成API授权token"""
    def post(self, request):
        body = json.loads(request.body.decode("utf-8"))
        try:
            username = body['username']
            password = body['password']
            if (username == settings.API_USERNAME
                    and password == settings.API_PASSWORD):
                payload = {
                    'iss': 'ssrmgmt',
                    'name': 'mgr',
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                return JsonResponse({'result': 'success', 'access_token': token.decode('utf-8')})
            else:
                return JsonResponse({'result': 'fail'})
        except Exception as e:
            logging.error("""生成api授权token时出现错误:{}""".format(e))
            return JsonResponse({'result': 'error'})

