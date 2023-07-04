from rest_framework import generics, permissions
from .models import Folder, File
from .serializers import FolderSerializer, FileSerializer, SharedFolderSerializer
import json

# Create your views here.
'''Folder API'''
class FolderList(generics.ListCreateAPIView):
    # a view for view user's created folders
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

class FolderList(generics.CreateAPIView):
    # a view for creating folders
    queryset = Folder.objects.filter()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

class FolderDetail(generics.RetrieveUpdateDestroyAPIView):
    # a view for retrieving, updating and deleting a folder by creator
    # queryset = Folder.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        body = self.request.body.decode()
        content = json.loads(body)
        folder = content.get('folder_name')
        return File.objects.filter(user=self.request.user, folder=folder)

class SharedFolderDetail(generics.RetrieveAPIView):
    permission_classes =  [permissions.AllowAny] # password required
    serializer_class = FileSerializer
    def get_queryset(self):
        body = self.request.body.decode()
        content = json.loads(body)
        name = content.get('folder_name')
        password = content.get('password')
        folder = Folder.objects.filter(name=name,password=password)
        return File.objects.filter(folder=folder)

'''File API'''
class FileList(generics.ListCreateAPIView):
    # a view for listing and creating files
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    # a view for retrieving, updating and deleting a file
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
