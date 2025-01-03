from .base import *

# enable oad
os.environ.setdefault('OAD_ENABLE', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyShare.settings.test')

ALLOWED_HOSTS = ['127.0.0.1','hailin545.cn','luohailin.cn','localhost','47.113.193.7','surgery.carnation.cloud-ip.biz']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
        "TIMEOUT": 60 * 60 * 3,
    }
}

# celery configuration
app.conf.update(
    broker_url='redis://redis:6379/6',
    result_backend='redis://redis:6379/7',
    timezone='Asia/Shanghai',
    worker_cancel_long_running_tasks_on_connection_loss=True,
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,
    worker_concurrency=2,  # cpu cores
    worker_prefetch_multiplier=1,  # default 4
    worker_max_tasks_per_child=10,  # after work 10 tasks, worker will be terminated
    task_track_started=True,
    broker_connection_retry_on_startup = True,
)
