from random import Random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings

# from users.models import EmailVerifyRecord


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
                cache.set(key, verify_code, 60 * 15)
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
                cache.set(key, verify_code, 60 * 15)
                return "email_send_ok"
            else:
                return "email_send_fail"


def send_active_email(email):
    verify_code = create_code(4)
    key = email
    link = settings.USER_DOMAIN + r"/users/activate" + "?email={}&code={}".format(email, verify_code)
    if key in cache:
        return "resend"
    else:
        email_title = "SSRMGMT用户激活邮件"
        email_body = "激活链接:{0}\n有效时间1小时".format(link)
        status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if status:
            # 发送成功就把验证码存入redis，有效时间
            cache.set(key, verify_code, 60 * 60)
            return "ok"
        else:
            return "fail"


def send_reset_pwd_email(email):
    verify_code = create_code(4)
    key = email + "_resetpwd"
    link = settings.USER_DOMAIN + r"/users/resetpwd" + "?email={}&code={}".format(email, verify_code)
    if key in cache:
        return "resend"
    else:
        email_title = "SSRMGMT重置密码"
        email_body = "重置链接:{0}\n有效时间1小时".format(link)
        status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if status:
            # 发送成功就把验证码存入redis，有效时间
            cache.set(key, verify_code, 60 * 60)
            return "ok"
        else:
            return "fail"

# if __name__ == '__main__':
#     print(create_code(4))
