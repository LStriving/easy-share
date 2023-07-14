from rest_framework import serializers
from .models import Folder, File

# Create your serializers here.

class FolderSerializer(serializers.ModelSerializer):
    # a serializer for the Folder model
    class Meta:
        model = Folder
        exclude = ['user']

class SharedFolderSerializer(serializers.ModelSerializer):
    # a serializer for the Folder model
    class Meta:
        model = Folder
        exclude = ['password']

class FileSerializer(serializers.ModelSerializer):
    # a serializer for the File model
    class Meta:
        model = File
        exclude = ['md5']

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['upload']
