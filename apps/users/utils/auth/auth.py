import hashlib

import jwt
from django.conf import settings
from django.utils.encoding import smart_text
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from users.models import UserProfile
from .utils import jwt_decode_handler


class BaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        print(jwt_value)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = _('Invalid Token.')
            raise exceptions.AuthenticationFailed(msg)

        user = self.authenticate_credentials(payload)
        print(user)
        return (user, payload)

    def get_jwt_value(self, request):
        raise NotImplementedError('get_jwt_value need to be Implemented.')

    def authenticate_credentials(self, payload):
        user_id = payload.get('user_id')

        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user


class JWTAuthentication(BaseJWTAuthentication):

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        # auth = request.META.get("HTTP_AUTHORIZATION")
        auth_header_prefix = 'jwt'

        if not auth:
            return None
        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None
        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format('jwt', 'api')


# class Authentication(BaseAuthentication):
#     def authenticate(self,  request):
#         token = request._request.GET.get('token')
#         token_obj = Token.objects.filter(token=token).first()
#         if not token:
#             raise AuthenticationFailed('用户认证失败')
#
#         return (token_obj.user, token_obj)
#
#     def authenticate_header(self, request):
#         pass
#
