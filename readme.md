# Easy Share

## Clone the project

```bash
# clone with submodules
git clone --recurse-submodules <project-url>
# or
git clone <project-url>
git submodule update --init --recursive # if you wish to use the machine learning model
```

### Large file

Install [git lfs](https://git-lfs.com/) to clone large file for the machine learning model

```bash
# clone large file (if you have git lfs installed)
git lfs install
git lfs pull
```

## Installation for Local

### Optional

```bash
conda create -n dj python=3.10
conda activate dj
```

### Requirements install

```bash
pip install -r requirements.txt
pip install -U channels["daphne"] #channels (for websocket)
pip install nvidia-ml-py3 # for gpu monitoring
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

## Installation for Docker

```bash
GITHUB_TOKEN={your_personal_access_token} docker-compose build
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
- [x] Large file removal strategy
- [ ] Fix lacking port for media url when deploying on Docker
- [x] lock redis cache for concurrent upload
- [ ] Multiple upload
- [ ] Prevent failed upload file from opening other sites from the users / Decrease the waiting time
- [ ] Task Site
