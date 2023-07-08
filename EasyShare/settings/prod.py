from .base import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE','EasyShare.settings.prod')

CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['127.0.0.1']

DEBUG = False

# https
SECURE_SSL_REDIRECT = False

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

# celery configuration
app.conf.update(
    broker_url='redis://127.0.0.1:6379/8',
    result_backend='redis://127.0.0.1:6379/9',
    timezone='Asia/Shanghai',
    worker_cancel_long_running_tasks_on_connection_loss=True,
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,
    worker_concurrency=8,  # cpu cores
    worker_prefetch_multiplier=2,  # default 4
    worker_max_tasks_per_child=10,  # after work 10 tasks, worker will be terminated

)