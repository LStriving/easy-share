from rest_framework import serializers
from .models import Folder, File

# Create your serializers here.

class FolderSerializer(serializers.ModelSerializer):
    # a serializer for the Folder model
    class Meta:
        model = Folder
        fields = '__all__'

class SharedFolderSerializer(serializers.ModelSerializer):
    # a serializer for the Folder model
    class Meta:
        model = Folder
        exclude = ['password']

class FileSerializer(serializers.ModelSerializer):
    # a serializer for the File model
    class Meta:
        model = File
        exclude = ['user']
