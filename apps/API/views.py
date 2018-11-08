import json
import logging

from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings

from users.models import UserProfile, SSRAccount, DataUsageRecord
from node import models
from apps.utils.mixin import VerifyAPITokenMixin

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
class NodeAlive(VerifyAPITokenMixin, View):
    """
    更新节点是否在线
    """
    def post(self, request):
        try:
            node_status = json.loads(request.body.decode("utf-8"))
            node = node_status['node']
            status = {
                'status': node_status['status'],
                'port_status': node_status['ports']
            }
            key = "node_online"
            if key in cache:
                node_online = cache.get(key)
            else:
                node_online = dict()
            node_online[node] = status
            # 设置60s的存活时间，需要节点不断上报数据
            cache.set('node_online', node_online, 60)
            print(node_online)
            return JsonResponse({'res': 'ok'})
        except KeyError as e:
            pass
            return JsonResponse({'res': 'fail'})


@method_decorator(csrf_exempt, name="dispatch")
class Transfer(VerifyAPITokenMixin, View):
    """
    存储用户流量信息
    """
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


@method_decorator(csrf_exempt, name="dispatch")
class NodeTransfer(VerifyAPITokenMixin, View):
    """
    存储主机流量
    """
    def post(self, request):
        node_io = json.loads(request.body.decode("utf-8"))
        node_id = node_io['node_id']
        recv = node_io['recv']
        sent = node_io['sent']
        try:
            node = models.Node.objects.filter(node_id=node_id)
            if node:
                node = node[0]
                data_usage = models.DataUsageRecord()
                data_usage.node = node
                data_usage.bytes_sent = sent
                data_usage.bytes_recv = recv
                data_usage.save()
                return JsonResponse({'res': 'ok'})
            else:
                return JsonResponse({'res': 'fail'})
        except Exception as e:
            return JsonResponse({'res': 'fail'})


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

