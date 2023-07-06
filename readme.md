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
python manage.py migirate
```

```bash
python manage.py collectstatic
```

```bash
python manage.py runserver
```

### Email

Use email function: create file name `.env` under `EasyShare/` folder
```
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
SECRET_KEY=
```
> Remember not to leave space in `.env` file

## TODO

- [ ] Large file chunked upload
- [x] Api auth
- [x] Api test by file
- [ ] User System
- [ ] Multiple working envs
- [ ] Nginx Deploy
