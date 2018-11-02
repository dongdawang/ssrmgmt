from functools import wraps

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.conf import settings

import jwt


class LoginRequireMixin(object):
    """判断是否登录
    """
    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, request, *args, **kwargs):
        """dispatch函数是用来处理请求路径的
        :param request: HttpResponse
        :param args: list
        :param kwargs: dict
        :return:
        """
        return super(LoginRequireMixin, self).dispatch(request, *args, **kwargs)


def api_verify():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = args[0]
            try:
                # django中http请求的原始部分的都被加上HTTP开头
                token = request.META.get("HTTP_AUTHORIZATION")
                if not token:
                    return HttpResponse('Unauthorized', status=401)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                # payload中的信息需要根据创建token时的payload来确定
                print(token)
                print(request)
                if payload['iss'] == 'ssrmgmt' and payload['name'] == 'mgr':
                    return func(*args, **kwargs)
                else:
                    return HttpResponse('Unauthorized', status=401)
            except KeyError as e:
                # 返回未认证的http响应
                return HttpResponse('Unauthorized', status=401)
            except jwt.exceptions.DecodeError as e:
                return HttpResponse('Unauthorized', status=401)
        return wrapper
    return decorator


class VerifyAPITokenMixin(object):
    """判断请求API的用户是否被授权"""
    @method_decorator(api_verify())
    def dispatch(self, request, *args, **kwargs):
        """dispatch函数是用来处理请求路径的
        :param request: HttpResponse
        :param args: list
        :param kwargs: dict
        :return:
        """
        return super(VerifyAPITokenMixin, self).dispatch(request, *args, **kwargs)

