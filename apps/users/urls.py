from django.urls import path
from django.contrib.auth.views import logout
from django.conf import settings

from .views import (Index, Login, Register, Profile, ModifyPwd, SendEmailCode, UserCharts, ModifyShow,
                    AccountEdit, AccountProfilePhotoModify, AccountPwdModify, AccountGeneralModify,
                    AccountNameModify, AccountSSRModify, AccountEmailModify, ProfileShow, ProfileCenter,
                    WorkOrderShow, WorkOrderAdd, WorkorderView, WorkorderDelete, BuyTime, TradeRecodeShow)


urlpatterns = [
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
    path('workorder/view/<int:wo_id>', WorkorderView.as_view(), name='workorder-view'),
    path('buy/time', BuyTime.as_view(), name='buy-time'),
    path('buy/recordshow', TradeRecodeShow.as_view(), name='record-show')
]