from django.urls import path

from .views import User, Transfer


urlpatterns = [
    path('user/', User.as_view(), name='user'),
    path('transfer/', Transfer.as_view(), name='transfer')
]
