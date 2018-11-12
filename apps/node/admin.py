from django.contrib import admin

from .models import Node, DataUsageRecord


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'node_id', 'name', 'ip']
    ordering = ['id']
    list_filter = ['id', 'node_id', 'name', 'ip']


@admin.register(DataUsageRecord)
class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'node', 'bytes_recv', 'bytes_sent', 'add_time']
    ordering = ['id']
    list_filter = ['id', 'node__node_id', 'bytes_recv', 'bytes_sent', 'add_time']
