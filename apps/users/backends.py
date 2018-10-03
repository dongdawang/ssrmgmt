from django.db.models import Q
from django.contrib.auth.backends import ModelBackend

from users.models import UserProfile

# class EmailBackend(object):
#     """
#     通过邮箱来登录
#     """
#     def authenticate(self, username=None, password=None):
#         try:
#             user = UserProfile.objects.get(eamil=username)
#             if user.check_password(password):
#                 return user
#             return None
#         except UserProfile.DoesNotExist:
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return UserProfile.objects.get(pk=user_id)
#         except UserProfile.DoesNotExist:
#             return None


# 设置邮箱、用户名都可以登录
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # 用Q进行并集查询（或操作）
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None
