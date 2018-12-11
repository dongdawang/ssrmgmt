from django.urls import path
from django.contrib.auth.views import logout
from django.conf import settings

from .views import (SendEmailCode, System, Activate, ResetPwd,
                    AccountEdit, AccountProfilePhotoModify, AccountPwdModify, AccountGeneralModify, ResetPwdEmail,
                    AccountNameModify, AccountSSRModify, AccountEmailModify, ProfileCenter,
                    WorkOrderShow, WorkOrderAdd, WorkorderView, WorkorderDelete, BuyTime, TradeRecodeShow,
                    Tutorial)

from users.utils.auth.views import ObtainJWTView, RefreshJWTView
from .views import (RegisterView, ProfileView, SSRAccountView, OnlineIPView, DataUsageView,
                    ProfilePhotoView)

urlpatterns = [
    path('login/', ObtainJWTView.as_view(), name='login'),
    path('logout/', logout, {'next_page': settings.LOGOUT_REDIRECT_URL}, name="logout"),
    path('refresh/', RefreshJWTView.as_view()),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('ssr/', SSRAccountView.as_view(), name='ssr'),
    path('onlineip/', OnlineIPView.as_view(), name='onelineip'),
    path('datausage/', DataUsageView.as_view(), name='datausage'),
    path('profilephoto/', ProfilePhotoView.as_view(), name='profilephoto'),

    path('resetpwd/', ResetPwd.as_view(), name='resetpwd'),
    path('resetpwdemail/', ResetPwdEmail.as_view(), name='resetpwdemail'),
    path('system/', System.as_view(), name='system'),
    path('profile/send-mail', SendEmailCode.as_view(), name='send_mail'),
    path('profile/account_edit', AccountEdit.as_view(), name='account_edit'),
    path('account/profile_photo_modify', AccountProfilePhotoModify.as_view(), name="photo_modify"),
    path('account/modify-pwd', AccountPwdModify.as_view(), name='modify-pwd'),
    path('account/modify-general', AccountGeneralModify.as_view(), name='modify-general'),
    path('account/modify-username', AccountNameModify.as_view(), name='modify-username'),
    path('account/modify-ssr', AccountSSRModify.as_view(), name='modify-ssr'),
    path('account/modify-email', AccountEmailModify.as_view(), name='modify-email'),
    path('profile/center', ProfileCenter.as_view(), name='profile-center'),
    path('workorder/show', WorkOrderShow.as_view(), name='workorder-show'),
    path('workorder/add', WorkOrderAdd.as_view(), name='workorder-add'),
    path('workorder/delete/<int:wo_id>', WorkorderDelete.as_view(), name='workorder-delete'),
    path('workorder/view/<int:wo_id>', WorkorderView.as_view(), name='workorder-view'),
    path('buy/time', BuyTime.as_view(), name='buy-time'),
    path('buy/recordshow', TradeRecodeShow.as_view(), name='record-show'),
    path('usage/tutorial/', Tutorial.as_view(), name='tutorial')
]
