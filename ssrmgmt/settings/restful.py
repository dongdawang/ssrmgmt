"""
REST_FRAMEWORK的配置项
"""


REST_FRAMEWORK = {
    # 全局配置认证类
    # 会调用Authtication.authticate方法，将认证信息存到request(drf的request)中
    'DEFAULT_AUTHENTICATION_CLASSES': ['users.utils.auth.auth.JWTAuthentication'],
    'DEFAULT_RENDER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'VERSION_PARAM': 'version',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': 'v1',
}
