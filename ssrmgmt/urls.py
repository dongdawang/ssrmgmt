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
from django.contrib.auth.views import logout

from users.views import (Index, Login, Register, Profile, ModifyPwd, SendEmailCode, UserCharts, ModifyShow,
                         AccountEdit, AccountProfilePhotoModify, AccountPwdModify, AccountGeneralModify,
                         AccountNameModify, AccountSSRModify, AccountEmailModify, ProfileShow, ProfileCenter,
                         WorkOrderShow, WorkOrderAdd, WorkorderView, WorkorderDelete)
from API.views import (User)
# from ssrmgmt.settings import MEDIA_ROOT

users_url = [
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout, {'next_page': settings.LOGOUT_REDIRECT_URL}, name="logout"),
    path('register/', Register.as_view(), name='register'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/send-mail', SendEmailCode.as_view(), name='send_mail'),
    path('profile/charts', UserCharts.as_view(), name='usercharts'),
    path('profile/modifyshow', ModifyShow.as_view(), name='modifyshow'),
    path('profile/account_edit', AccountEdit.as_view(), name='account_edit'),
    path('account/profile_photo_modify', AccountProfilePhotoModify.as_view(), name="photo_modify"),
    path('account/modify-pwd', AccountPwdModify.as_view(), name='modify-pwd'),
    path('account/modify-general', AccountGeneralModify.as_view(), name='modify-general'),
    path('account/modify-username', AccountNameModify.as_view(), name='modify-username'),
    path('account/modify-ssr', AccountSSRModify.as_view(), name='modify-ssr'),
    path('account/modify-email', AccountEmailModify.as_view(), name='modify-email'),
    path('profile/show', ProfileShow.as_view(), name='profile-show'),
    path('profile/center', ProfileCenter.as_view(), name='profile-center'),
    path('workorder/show', WorkOrderShow.as_view(), name='workorder-show'),
    path('workorder/add', WorkOrderAdd.as_view(), name='workorder-add'),
    path('workorder/delete/<int:wo_id>', WorkorderDelete.as_view(), name='workorder-delete'),
    path('workorder/view/<int:wo_id>', WorkorderView.as_view(), name='workorder-view')
]

api_url = [
    path('user/', User.as_view(), name='user'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    # 创建一个命名空间，可以有效的对url进行分类
    path('users/', include((users_url, "users")), name='users'),
    path('api/', include((api_url, "API")), name='api'),
    # path('media/<str>', serve, {"document_root": MEDIA_ROOT})
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


