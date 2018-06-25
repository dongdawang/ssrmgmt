from django.urls import path

from users.views import Login


urlpatterns = [
    path('login', Login.as_view()),
]