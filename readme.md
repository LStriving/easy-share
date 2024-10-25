# Easy Share

Django project for surgery video analysis, containing apps with function:
    - **administration**
    - **sharefiles (upload large files)**
    - **offline model prediction**
    <!-- **online prediction**(websocket), -->

## Get Started

### Clone the project

```bash
# clone with submodules
git clone --recurse-submodules <project-url>
# or
git clone <project-url>
git submodule update --init --recursive # if you wish to use the machine learning model
```

### Download Large file (Optional)

Install [git lfs](https://git-lfs.com/) to clone large file for the machine learning model checkpoint.

```bash
# clone large file (if you have git lfs installed)
git lfs install
git lfs pull
```

### Start with Local

```bash
conda create -n dj python=3.10
conda activate dj
```

#### (Optional) Download Checkpoints

If you want to use the machine learning model, you need to download the checkpoints for the model.

```bash
cd ./apps/surgery/libs/oad
git lfs install
git lfs pull
cd ../seg
git lfs install
git lfs pull
```

#### Install Requirements

```bash
pip install -r requirements.txt
pip install -U channels["daphne"] #channels (for websocket)
```

#### Prepare database for Server

```bash
python manage.py makemigrations access sharefiles
```

```bash
python manage.py migrate
```

```bash
python manage.py collectstatic
```

#### Email

Use email function: create file name `.env` under `EasyShare/settings` folder

```.env
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SECRET_KEY=
```

> Remember not to leave space in `.env` file

#### Redis

#### Celery

##### Local

```bash
celery -A EasyShare worker
celery -A EasyShare beat
```

##### Deploy

```bash
# Start worker
celery -A EasyShare worker -c gevent
# Start beat (schedule task)
celery -A EasyShare beat
```

#### Start Server

```bash
python manage.py runserver
```

### Start with Docker

Github token is required for downloading the submodules(external repositories)

```bash
GITHUB_TOKEN={your_personal_access_token} docker-compose build --shm-size=16GB
```

Remember to set SRECET_KEY and EMAIL in the `.env` file

### Remote forward

```bash
# ssh -R remote_port:localhost:local_port ssh_server_hostname
ssh -NfR 4999:localhost:3344 root@luohailin.cn -o ServerAliveInterval=60  # no shell and background
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
- [x] Logo url
- [x] User guidance manual
- [x] Large file removal strategy
- [x] Fix lacking port for media url when deploying on Docker
- [x] lock redis cache for concurrent upload
- [ ] Multiple upload
- [x] Prevent failed upload file from opening other sites from the users / Decrease the waiting time
- [x] Task Site
- [x] smarter way for loading model and calling predict
- [x] add hint for loading video
- [x] hold icons in local
- [ ] add notification feature
- [ ] en/zh switch
- [x] view task logs
- [x] compress model checkpoint (comsume more space when using onnx)
