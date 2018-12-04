from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from node.models import Node
from users.models import SSRAccount
from apps.utils.nodemgr import NodeStatusCacheMgr


class NodeSerializer(ModelSerializer):
    status = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    detail = serializers.HyperlinkedIdentityField(
        view_name='node:node-detail', lookup_field='node_id', lookup_url_kwarg='n_id')

    class Meta:
        model = Node
        fields = ['id', 'node_id', 'name', 'ip', 'status', 'count', 'detail']

    def get_status(self, obj):
        nscm = NodeStatusCacheMgr()
        return nscm.get_node_status(obj.node_id)

    def get_count(self, obj):
        return SSRAccount.objects.filter(node=obj).count()
