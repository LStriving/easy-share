import os
import platform

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyShare.settings.dev')
if platform.platform().__contains__('Windows'):
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
app = Celery('EasyShare')
app.config_from_object('django.conf:settings')
# 自动注册worker函数
app.autodiscover_tasks()