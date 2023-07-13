pkill -f celery
nohup celery -A EasyShare worker > log/celery.log &
