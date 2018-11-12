from django.contrib import admin

from .models import (UserProfile, SSRAccount, UserModifyRecord, Announcement, WorkOrder, DataUsageRecord,
                     TradeRecord)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'nick_name', 'birthday', 'gender', 'email', 'mobile', 'address', 'date_joined']
    ordering = ['date_joined']
    list_filter = ['username', 'nick_name', 'birthday', 'gender', 'email', 'mobile', 'address', 'date_joined']


@admin.register(SSRAccount)
class SSRAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'expiration_time', 'port', 'passwd', 'method', 'protocol', 'obfs', 'compatible', 'node', 'user']
    ordering = ['id']
    list_filter = ['id', 'expiration_time', 'port', 'passwd', 'method', 'protocol', 'obfs', 'compatible',
                   'node__node_id', 'user__username']
    pass


@admin.register(UserModifyRecord)
class UserModifyRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'modify_type', 'add_time']
    ordering = ['id']
    list_filter = ['id', 'user__username', 'modify_type', 'add_time']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'body']
    ordering = ['id']
    list_filter = ['id', 'time', 'body']


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'body', 'status', 'add_time']
    ordering = ['id']
    list_filter = ['id', 'user__username', 'title', 'body', 'status', 'add_time']


@admin.register(DataUsageRecord)
class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'ssr', 'bytes_received', 'bytes_sent', 'add_time']
    ordering = ['id']
    list_filter = ['id', 'ssr__port', 'bytes_received', 'bytes_sent', 'add_time']


@admin.register(TradeRecord)
class TradeRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'time', 'add_time']
    ordering = ['id']
    list_filter = ['id', 'user__username', 'amount', 'time', 'add_time']
