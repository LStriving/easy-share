from django.db import models

from access.models import User


class Folder(models.Model):
    # a model for shared folders
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255,null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    # a many-to-many relationship with the file model

class File(models.Model):
    # a model for uploaded files
    name = models.CharField(max_length=255)
    size = models.IntegerField()
    type = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    # the uploader
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    # upload to MEDIA_ROOT/uploads/
    upload = models.FileField(upload_to=f"uploads/{folder}")
    # a foreign key to the user who uploaded the file


