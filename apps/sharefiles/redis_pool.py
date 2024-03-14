import redis
import os
env = os.environ.get("DJANGO_SETTINGS_MODULE").split('.')[-1]
if env == 'dev' or env == 'prod':
    host = '127.0.0.1'
else:
    host = 'redis'
POOL=redis.ConnectionPool(host=host,port=6379,max_connections=100)
