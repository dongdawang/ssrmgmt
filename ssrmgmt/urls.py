"""ssrmgmt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

from users.views import (Index, Login, Register, Profile, ProfilePhotoUpload,
                         ModifyPwd, ModifyEmail, SendEmailCode)
from goods.views import Ping
from operation.views import CreateAccount
# from ssrmgmt.settings import MEDIA_ROOT

users_url = [
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/profile-photo', ProfilePhotoUpload.as_view(), name='profile-photo'),
    path('profile/modify-pwd', ModifyPwd.as_view(), name='modify-pwd'),
    path('profile/modify-email', ModifyEmail.as_view(), name='modify-email'),
    path('profile/send-mail', SendEmailCode.as_view(), name='send_mail'),
]

operation_url = [
    path('createaccount/<str:ip>', CreateAccount.as_view(), name='create_account'),
    path('createaccount/', CreateAccount.as_view(), name='create_account'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    path('ping', Ping.as_view(), name='ping'),
    # 创建一个命名空间，可以有效的对url进行分类
    path('users/', include((users_url, "users")), name='users'),
    # path('media/<str>', serve, {"document_root": MEDIA_ROOT})
    path('operation/', include((operation_url, 'operation')), name='operation')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


