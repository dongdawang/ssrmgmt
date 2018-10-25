from django.shortcuts import render
from django.views import View

from .models import Node
from apps.utils.mixin import LoginRequireMixin


class NodeShow(LoginRequireMixin, View):
    """显示节点列表"""
    def get(self, request):
        nodes = Node.objects.all()
        params = {
            'nodes': nodes,
        }
        return render(request, 'backend/usage/nodelist.html', params)

