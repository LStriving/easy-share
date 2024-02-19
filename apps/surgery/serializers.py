from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    file = serializers.StringRelatedField()
    class Meta:
        model = Task
        exclude = ['user']