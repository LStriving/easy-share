from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    # inherit from the built-in user model
    email = models.EmailField(unique=True)

admin.site.register(User)

class EmailCode(models.Model):
    email = models.EmailField(max_length=254,primary_key=True)
    code = models.CharField(max_length=6)
    updated_time = models.DateTimeField(auto_now=True)