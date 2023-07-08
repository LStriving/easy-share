from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    # inherit from the built-in user model
    email = models.EmailField(unique=True)

admin.site.register(User)