from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from .models import Node, DataUsageRecord
from apps.utils.mixin import LoginRequireMixin
from users.models import SSRAccount
from apps.utils.nodemgr import NodeStatusCacheMgr


class NodeShow(LoginRequireMixin, View):
    """显示节点列表"""
    def get(self, request):
        nodes = Node.objects.all()
        nscm = NodeStatusCacheMgr()
        node_info = []
        for node in nodes:
            count = SSRAccount.objects.filter(node=node).count()
            # stat is 'offline' or 'online'
            stat = nscm.get_node_status(node.node_id)
            node_info.append({'node': node, 'count': count, 'status': stat})

        user = request.user
        ssr = SSRAccount.objects.get(user=user)
        curr_node = ssr.node
        params = {
            'curr_node': curr_node,
            'node_info': node_info,
        }
        return render(request, 'backend/usage/nodelist.html', params)


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


class NodeDetail(LoginRequireMixin, View):
    """显示节点详情"""

    def get(self, request, n_id):
        node = Node.objects.get(node_id=n_id)
        nscm = NodeStatusCacheMgr()
        usages = DataUsageRecord.last_30_days(node)
        acounts = SSRAccount.objects.filter(node=node)
        count = len(acounts)
        online_count = 0
        for acount in acounts:
            if nscm.get_port_ips(acount.port):
                online_count += 1
        params = {
            'usages': usages,
            'user': {
                'total': count,
                'online': online_count,
                'online_rate': 0 if count == 0 else online_count*100//count
            }
        }
        return render(request, 'backend/usage/nodedetail.html', params)
