from random import Random
from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from django.conf import settings


def create_code(code_len=8):
    code_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(code_len):
        code_str += chars[random.randint(0, length)]
    return code_str


def send_type_email(email, send_type='register'):
    email_record = EmailVerifyRecord()
    email_record.code = create_code(4)
    email_record.send_type = send_type
    email_record.email = email
    email_record.save()

    email_title = ""
    email_body = ""

    if send_type == "modify_email":
        email_title = "SSRMGMT邮箱修改验证码"
        email_body = "验证码:{0}".format(email_record.code)

        status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if status:
            pass


# if __name__ == '__main__':
#     print(create_code(4))

