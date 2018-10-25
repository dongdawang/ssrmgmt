"""ssrmgmt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

from users.views import Index
# from ssrmgmt.settings import MEDIA_ROOT


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    # 创建一个命名空间，可以有效的对url进行分类
    path('users/', include(("users.urls", "users"), namespace="users")),
    path('api/', include(("API.urls", "API"), namespace="api")),
    path('node/', include(("node.urls", "node"), namespace="node")),
    # path('media/<str>', serve, {"document_root": MEDIA_ROOT})
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


