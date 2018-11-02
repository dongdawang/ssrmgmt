from django.urls import path

from .views import User, Transfer, NodeAlive, NodeTransfer, GenerateToken


urlpatterns = [
    path('user/', User.as_view(), name='user'),
    path('transfer/', Transfer.as_view(), name='transfer'),
    path('node/status/', NodeAlive.as_view(), name='status'),
    path('node/transfer/', NodeTransfer.as_view(), name='node_transfer'),
    path('node/token/generate/', GenerateToken.as_view())
]
