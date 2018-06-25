from django.contrib import admin

from .models import SsrAccount, SsrServer


class SsrAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_name', 'ip', 'port', 'add_time']
    ordering = ['account_name', 'add_time']
    search_fields = ['user__nick_name', 'account_name', 'ip', 'port', 'add_time']


class SsrServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'ip', 'Weights', 'is_enable', 'add_time']
    ordering = ['add_time']
    search_fields = ['name', 'address', 'ip', 'Weights', 'is_enable', 'add_time']


admin.site.register(SsrAccount, SsrAccountAdmin)
admin.site.register(SsrServer, SsrServerAdmin)
