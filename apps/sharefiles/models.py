from django.db import models
from django.contrib import admin
from access.models import User
import os


class Folder(models.Model):
    # a model for shared folders
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=20,null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    # a many-to-many relationship with the file model

    def __str__(self) -> str:
        return self.name
    class Meta:
        ordering = ['id']
        unique_together = ('name','user')
        

def get_folder_name(instance, filename):
    return os.path.join('uploads', instance.folder.name, filename)

class File(models.Model):
    # a model for uploaded files
    name = models.CharField(max_length=255)
    size = models.IntegerField(help_text='File size (bytes)')
    type = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    # the uploader
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    # upload to MEDIA_ROOT/uploads/
    upload = models.FileField(upload_to=get_folder_name)
    # a foreign key to the user who uploaded the file
    md5 = models.CharField(max_length=32,null=True)
    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


admin.site.register(Folder)
admin.site.register(File)
