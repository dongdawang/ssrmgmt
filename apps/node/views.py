from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from .models import Node, DataUsageRecord
from apps.utils.mixin import LoginRequireMixin
from users.models import SSRAccount


class NodeShow(LoginRequireMixin, View):
    """显示节点列表"""
    def get(self, request):
        nodes = Node.objects.all()

        key = "node_online"
        if key in cache:
            # node_online结构
            # node_online是一个字典，其中key为node，node是node_id的意思
            # node_online[node_id]获取一个字典status
            # status中key: status->online or offline
            #              port_status: 字典
            #
            # node_online = {
            #     'node_id': {
            #         'status': 'online' or 'offline',
            #         'port_status': {
            #             'port': ['在这个端口上的ip'],
            #             ...
            #         }
            #     },
            #     ...
            # }
            node_online = cache.get(key)
        else:
            node_online = None

        node_info = []
        for node in nodes:
            count = SSRAccount.objects.filter(node=node).count()
            stat = 'offline'
            if node_online:
                try:
                    # 获取这个节点的状态，节点状态默认是offline
                    stat = node_online[node.node_id]['status']
                except Exception as e:
                    pass
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
        usages = DataUsageRecord.last_30_days(node)
        params = {
            'usages': usages,
        }
        return render(request, 'backend/usage/nodedetail.html', params)
