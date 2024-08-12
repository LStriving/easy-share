from django.db import models
from access.models import User
from django.contrib import admin

# Create your models here.
# Task model with user, task name, task status, task result url, task created time, file
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    task_status = models.CharField(max_length=100)
    task_result_url = models.CharField(max_length=100)
    task_created_time = models.DateTimeField(auto_now_add=True)
    file = models.OneToOneField('sharefiles.File', on_delete=models.CASCADE)
    def __str__(self):
        return self.task_name + " " + self.file.name
    
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id','task_name', 'task_status', 'task_result_url', 'task_created_time')
    search_fields = ('id','task_name', 'task_status', 'task_result_url', 'task_created_time')
    list_filter = ('id','task_name', 'task_status', 'task_result_url', 'task_created_time')
    ordering = ('id','task_name', 'task_status', 'task_result_url', 'task_created_time')

admin.site.register(Task, TaskAdmin)