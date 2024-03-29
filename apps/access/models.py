from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser

from .managers import UserManager
# Create your models here.

class User(AbstractUser):
    # inherit from the built-in user model
    email = models.EmailField(unique=True)
    storage = models.BigIntegerField(help_text="Users' uploaded amount",default=0)
    objects = UserManager()

admin.site.register(User)