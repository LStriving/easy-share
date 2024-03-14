"""
Django settings for EasyShare project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import sys
import os
import environ
from EasyShare.celery import app
from celery.schedules import crontab

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
SECRET_KEY = env('SECRET_KEY')

sys.path.insert(0,os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['luohailin.cn', 'localhost','127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['http://luohailin.cn:4080','http://luohailin.cn:4070',r'http://luohailin.cn:\d+/']
# Daphne
ASGI_APPLICATION = 'EasyShare.asgi.application'
# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'apps.access',
    'apps.sharefiles',
    'apps.video_rtc',
    'apps.surgery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'EasyShare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            },  
        },
        
    },
]

WSGI_APPLICATION = 'EasyShare.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/surgery'  # Redirect to the home page after login
LOGOUT_REDIRECT_URL = '/user/login'  # Redirect to the home page after logout

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = 'media/'

MEDIA_URL = 'media/'

STATIC_ROOT = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'apps/access/static'),
    os.path.join(BASE_DIR, 'apps/sharefiles/static'),
]

OAD_INPUNT_DIR = os.path.join(BASE_DIR, 'media/input_data/Surgery/') # should be the same as in the OAD model
EXTRACT_OUTPUT_DIR = os.path.join(OAD_INPUNT_DIR,'frames') # should be the same as in the OAD model
TARGET_DIR = os.path.join(OAD_INPUNT_DIR,'targets') # should be the same as in the OAD model
# settings for video prediction result
OAD_OUTPUT_URL = '/media/oad_output/'
OAD_FILE_OUTPUT_URL = '/media/oad_result/'
SEG_IMG_OUTPUT_URL = '/media/seg_img/'
SEG_VIDEO_OUTPUT_URL = '/media/seg_video/'
SEG_FILE_OUTPUT_URL = '/media/seg_result/'

OAD_DIR = os.path.join(BASE_DIR, '/apps/surgery/libs/oad')
OAD_CHECKPOINT = os.path.join(OAD_DIR, 'ckpt/checkpoint_epoch_00018.pyth')
OAD_OUTPUT_DIR = os.path.join(BASE_DIR, OAD_OUTPUT_URL[1:])
OAD_OUTPUT_NPY_DIR = os.path.join(BASE_DIR, OAD_OUTPUT_URL[1:] + 'npy')
OAD_FILE_OUTPUT_DIR = os.path.join(BASE_DIR, OAD_FILE_OUTPUT_URL[1:])
SEG_IMG_OUTPUT_DIR = os.path.join(BASE_DIR, SEG_IMG_OUTPUT_URL[1:])
SEG_VIDEO_OUTPUT_DIR = os.path.join(BASE_DIR, SEG_VIDEO_OUTPUT_URL[1:])
SEG_FILE_OUTPUT_DIR = os.path.join(BASE_DIR, SEG_FILE_OUTPUT_URL[1:])
FILE_1_POSTFIX = '_interact_1.txt'
FILE_8_POSTFIX = '_interact_8.txt'
PRE_FILE_POSTFIX = '_pro.txt'
PRE_DUR_FILE_POSTFIX = "_dur.txt"

GPU_DEVICE = 0
MAX_EXECUTING_TASK_AT_ONCE = 1

# channels
MAX_CONCURRENT_REQUESTS = 4

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'access.User'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_CODE_EXPIRED_TIME = 60 * 10 # 10MINS

MAX_HANDLE_FILE = 50

PER_USER_STORAGE_LIMIT = 1073741824 * 5 # 1GB * 5

# Celery Beat Task Scheduler
app.conf.beat_schedule = {
    # Executes every day at 00:00
    'remove-30days-tmp-file': {
        'task': 'sharefiles.utils.remove_tmp',
        'schedule': crontab(minute=0, hour=0)
    },
    # Executes every 5 minutes
    'model-prediction-task': {
        'task': 'surgery.tasks.get_task_n_work',
        'schedule': crontab(minute='*/5')
    },
}