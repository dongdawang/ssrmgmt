from django.urls import path

from .views import NodeShow

urlpatterns = [
    path('node/', NodeShow.as_view(), name='node-show'),
]