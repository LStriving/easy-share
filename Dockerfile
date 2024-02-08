FROM python:3.10

ENV PYTHONUNBUFFERED=1  
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN python manage.py collectstatic --noinput --settings=EasyShare.settings.test
RUN python manage.py makemigrations --empty access --settings=EasyShare.settings.test
RUN python manage.py makemigrations access sharefiles --settings=EasyShare.settings.test
