import jwt

from calendar import timegm
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.utils.translation import ugettext as _
from rest_framework import serializers

from .settings import api_settings

from .utils import jwt_decode_handler, jwt_encode_handler, jwt_get_secret_key, jwt_payload_handler


User = get_user_model()


class Serializer(serializers.Serializer):
    @property
    def object(self):
        return self.validated_data


class JWTSerializer(Serializer):
    """
    Serializer class used to validate a username and password.
    'username' is identified by the custom UserModel.USERNAME_FIELD.
    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(JWTSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = serializers.CharField()

    @property
    def username_field(self):
        return 'username'

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            # cu = CustomBackend()
            # user = cu.authenticate(**credentials)
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)
                print(payload)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class VerificationBaseSerializer(Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = payload.get('username')

        if not username:
            msg = _('Invalid payload.')
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise serializers.ValidationError(msg)

        return user


# class VerifyJSONWebTokenSerializer(VerificationBaseSerializer):
#     """
#     Check the veracity of an access token.
#     """
#
#     def validate(self, attrs):
#         token = attrs['token']
#
#         payload = self._check_payload(token=token)
#         user = self._check_user(payload=payload)
#
#         return {
#             'token': token,
#             'user': user
#         }


class RefreshJWTSerializer(VerificationBaseSerializer):
    """
    Refresh an access token.
    """

    def _check_payload(self, token):
        """重写父类的校验token的方法，不检验token是否过期，只校验签名"""
        try:
            payload = jwt_decode_handler(token, verify_exp=False)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

    def _check_blacklist(self, token):
        """检查token是否被拉入黑名单"""
        if cache.get('refresh_'+token):
            return True
        return False

    def _add_blacklist(self, token, exp_time):
        cache.set('refresh_'+token, 'black', exp_time)

    def validate(self, attrs):
        token = attrs['token']

        if self._check_blacklist(token):
            msg = _('Token has blacked.')
            raise serializers.ValidationError(msg)

        payload = self._check_payload(token=token)
        print(payload)
        user = self._check_user(payload=payload)
        # Get and check 'iat'
        orig_iat = payload.get('iat')
        print(orig_iat)
        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)

            # 将原来的token加入黑名单，避免再用原来的token获取新的token，同时设置缓存超时时间，自动清理
            exp_time = expiration_timestamp - now_timestamp
            self._add_blacklist(token, exp_time)
        else:
            msg = _('iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['iat'] = orig_iat

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }
