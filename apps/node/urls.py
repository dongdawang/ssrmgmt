from django.urls import path

from .views import NodeShow, NodeDetail, SelectNode

urlpatterns = [
    path('node/', NodeShow.as_view(), name='node-show'),
    path('node/detail/<int:n_id>', NodeDetail.as_view(), name='node-detail'),
    path('node/select/', SelectNode.as_view(), name='node-select')
]
