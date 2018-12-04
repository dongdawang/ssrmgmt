from django.urls import path

from .views import SelectNode, NodeView, DetailView

urlpatterns = [
    path('node/', NodeView.as_view(), name='node-all'),
    path('node/<int:n_id>/', NodeView.as_view(), name='node-per'),
    path('node/detail/<int:n_id>/', DetailView.as_view(), name='node-detail')
]
