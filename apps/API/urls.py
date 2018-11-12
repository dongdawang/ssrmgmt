from django.urls import path

from .views import User, UserTransfer, NodeStatus, NodeTransfer, GenerateToken


urlpatterns = [
    path('user/', User.as_view(), name='user'),
    path('transfer/', UserTransfer.as_view(), name='transfer'),
    path('node/status/', NodeStatus.as_view(), name='status'),
    path('node/transfer/', NodeTransfer.as_view(), name='node_transfer'),
    path('node/token/generate/', GenerateToken.as_view())
]
