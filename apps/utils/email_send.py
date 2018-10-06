from random import Random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

from users.models import EmailVerifyRecord


def create_code(code_len=8):
    code_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(code_len):
        code_str += chars[random.randint(0, length)]
    return code_str


def send_type_email(email, send_type='register'):
    verify_code = create_code(4)

    if send_type == "modify_email":
        # 发送验证码之前判断下是否已经发送
        key = email
        if key in cache:
            return "email_resend"
        else:
            email_title = "SSRMGMT修改邮箱验证码"
            email_body = "验证码:{0}，有效时间15分钟".format(verify_code)
            status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
            if status:
                # 发送成功就把验证码存入redis，有效时间
                cache.set(key, verify_code, 60 * 60 * 15)
                return "email_send_ok"
            else:
                return "email_send_fail"

    if send_type == "register":
        # 发送验证码之前判断下是否已经发送
        key = email
        if key in cache:
            return "email_resend"
        else:
            email_title = "SSRMGMT注册邮箱验证码"
            email_body = "验证码:{0}，有效时间15分钟".format(verify_code)
            status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
            if status:
                # 发送成功就把验证码存入redis，有效时间
                cache.set(key, verify_code, 60 * 60 * 15)
                return "email_send_ok"
            else:
                return "email_send_fail"


# if __name__ == '__main__':
#     print(create_code(4))
