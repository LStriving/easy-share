"""
URL configuration for EasyShare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import re_path as url
from django.urls import path,include
from rest_framework_swagger.views import get_swagger_view
from django.views.static import serve
from django.contrib.auth import views as auth_views

from EasyShare.settings.base import MEDIA_ROOT    # 导入相关静态文件处理的views控制包

schema_view = get_swagger_view(title='EasyShare API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('easyshare/',include('sharefiles.urls')),
    path("user/", include("access.urls")),
    path("rtc/",include("video_rtc.urls")),
    path("surgery/",include("surgery.urls")),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    url(r'^doc$', schema_view,name='documentation'),
    path("",include("surgery.urls")),
    # path("",auth_views.LoginView.as_view(template_name='./login.html'),name='login')
]
