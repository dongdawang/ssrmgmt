from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from .models import Node, DataUsageRecord
from apps.utils.mixin import LoginRequireMixin
from users.models import SSRAccount
from apps.utils.nodemgr import NodeStatusCacheMgr


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from node.utils.serializers import NodeSerializer


class NodeView(APIView):
    def get(self, request, *args, **kwargs):
        n_id = kwargs.get('n_id')
        if n_id:
            query_set = Node.objects.filter(node_id=n_id).first()
            sers = NodeSerializer(instance=query_set, many=False, context={'request': request})
        else:
            query_set = Node.objects.all()
            sers = NodeSerializer(instance=query_set, many=True, context={'request': request})
        return Response(sers.data)


class SelectNode(LoginRequireMixin, View):
    """修改用户在的节点"""
    def post(self, request):
        try:
            n_id = request.POST.get('n_id')
            node = Node.objects.get(node_id=n_id)
            user = request.user
            ssr = SSRAccount.objects.get(user=user)
            ssr.node = node
            ssr.save()
            return JsonResponse({'res': '修改节点成功'})
        except ObjectDoesNotExist:
            return JsonResponse({'res': '所选择节点已被删除'})


class DetailView(APIView):
    def get(self, request, *args, **kwargs):
        n_id = kwargs.get('n_id')
        node = Node.objects.get(node_id=n_id)
        nscm = NodeStatusCacheMgr()
        usages = DataUsageRecord.last_30_days(node)
        accounts = SSRAccount.objects.filter(node=node)
        code = 0
        count = len(accounts)
        online_count = 0
        for account in accounts:
            if nscm.get_port_ips(account.port):
                online_count += 1

        ret = {
            'code': code,
            'usage': usages,
            'user': {
                'total': count,
                'online': online_count,
                'online_rate': 0 if count == 0 else online_count * 100 // count
            }
        }

        return Response(ret)
