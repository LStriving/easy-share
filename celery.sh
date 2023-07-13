celery multi stop 1 -A EasyShare --pidfile=log/%n.pid --logfile=log/celery.log || true
celery multi start 1 -A EasyShare --logfile=log/celery.log -l info --pidfile=log/%n.pid
