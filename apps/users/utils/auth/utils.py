import jwt
import uuid
import warnings
import hashlib
from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from .settings import api_settings


def md5(ori_str):
    m = hashlib.md5(bytes(ori_str, encoding='utf-8'))
    return m.hexdigest()


def jwt_get_secret_key(payload=None):
    """根据用户的密码，然后加salt后md5加密"""
    User = get_user_model()
    user = User.objects.get(pk=payload.get('user_id'))
    key = str(md5(user.password + settings.SECRET_KEY))
    return key


def jwt_payload_handler(user):
    payload = {
        'user_id': user.pk,
        'username': user.username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr(user, 'email'):
        payload['email'] = user.email

    if api_settings.JWT_ALLOW_REFRESH:
        payload['iat'] = timegm(datetime.utcnow().utctimetuple())

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE
    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def jwt_encode_handler(payload):
    key = jwt_get_secret_key(payload)
    return jwt.encode(
        payload,
        key,
        api_settings.JWT_ALGORITHM
    ).decode('utf-8')


def jwt_decode_handler(token, verify_exp=True):
    options = {
        'verify_exp': verify_exp,
    }
    unverified_payload = jwt.decode(token, None, False)
    secret_key = jwt_get_secret_key(unverified_payload)
    return jwt.decode(
        token,
        key=secret_key,
        verify=True,
        options=options,
        leeway=api_settings.JWT_LEEWAY,  # 设置这个保证并发的时候，在token过期后的JWT_LEEWAY时间内，token依旧能使用
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )


