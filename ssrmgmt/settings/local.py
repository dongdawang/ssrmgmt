from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssrmgmt',
        'USER': get_env_variable('SSRMGMT_MYSQL_USER'),
        'PASSWORD': get_env_variable('SSRMGMT_MYSQL_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            # 取消外键检查
            "init_command": "SET foreign_key_checks = 0;",
        },
    }
}

# 设置django使用redis做缓存
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# 账户激活域名
USER_DOMAIN = "localhost:8080"

# API相关
API_USERNAME = get_env_variable('SSRMGMT_API_USERNAME')
API_PASSWORD = get_env_variable('SSRMGMT_API_PASSWORD')

# 邮箱设置
EMAIL_HOST = "smtp.163.com"
EMAIL_HOST_USER = get_env_variable('SSRMGMT_EMAIL_USER')
EMAIL_HOST_PASSWORD = get_env_variable('SSRMGMT_EMAIL_PASSWORD')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_FROM = "ssrmgmt@163.com"
