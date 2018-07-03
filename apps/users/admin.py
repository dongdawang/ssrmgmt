from django.contrib import admin

from .models import UserProfile, EmailVerifyRecord


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'nick_name', 'birthday', 'gender', 'address', 'mobile', 'date_joined']
    ordering = ['date_joined']
    list_filter = ['username', 'nick_name', 'birthday', 'gender', 'address', 'mobile', 'date_joined']


class EmailVerifyRecordAdmin(admin.ModelAdmin):
    list_display = ['code', 'email', 'send_type', 'send_time']
    ordering = ['send_time']
    list_filter = ['code', 'email', 'send_type', 'send_time']


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
