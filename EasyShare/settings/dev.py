from .base import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyShare.settings.dev')

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "TIMEOUT": 60 * 30, # 30 MINSS
    }
}


# celery configuration
app.conf.update(
    broker_url='redis://127.0.0.1:6379/3',
    result_backend='redis://127.0.0.1:6379/4',
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