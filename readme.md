# Easy Share

## Installation

### Optional

```bash
conda create -n dj python=3.10
conda activate dj
```

### Requirements install

```bash
pip install -r requirements.txt
```

```bash
python manage.py makemigrations access sharefiles
```

```bash
python manage.py migrate
```

```bash
python manage.py collectstatic
```

```bash
python manage.py runserver
```

### Email

Use email function: create file name `.env` under `EasyShare/settings` folder

```.env
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SECRET_KEY=
```

> Remember not to leave space in `.env` file

### Redis

### Celery

#### Local

```bash
celery -A EasyShare worker
```

#### Deploy

```bash
# Start worker
celery -A EasyShare worker -c gevent
# Start beat (schedule task)
celery -A EasyShare beat
```

## User Manual

[User Manual](user-guide.md)

## TODO

- [x] Large file chunked upload
- [x] Api auth
- [x] Api test by file
- [x] User System
- [x] Multiple working envs
- [x] Docker Deploy
- [ ] Logo url
- [x] User guidance manual
- [ ] Large file removal strategy
- [ ] Fix lacking port for media url when deploying on Docker
