FROM python:3.10

ENV PYTHONUNBUFFERED=1  
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U channels["daphne"]
RUN pip install pillow==10.2.0

COPY . /app

RUN python manage.py collectstatic --noinput --settings=EasyShare.settings.test
RUN python manage.py makemigrations --empty access --settings=EasyShare.settings.test
RUN python manage.py makemigrations access sharefiles --settings=EasyShare.settings.test
