from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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

