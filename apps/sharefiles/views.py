import shutil
from rest_framework import generics, permissions
from EasyShare.settings import MEDIA_ROOT
from .models import Folder, File
from .serializers import FolderSerializer, FileSerializer
from django.core.exceptions import ObjectDoesNotExist

import os

# Create your views here.
# passed
'''Folder API'''
class FolderList(generics.ListCreateAPIView):
    '''
        get:
            Return User's created folders
        
        post:
            Create a folder
    '''
    # a view for view user's created folders & creating folders
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Folder.objects.filter(creator=self.request.user)


class FolderFiles(generics.ListAPIView):
    '''
        get:
            View files of a folder
    '''
    # a view for viewing folder files by creators using folder_id
    serializer_class = FileSerializer
    lookup_field = 'folder_id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        folder = self.kwargs['folder_id']
        return File.objects.filter(user=self.request.user, folder=folder)
    
class FolderDelete(generics.DestroyAPIView):
    '''
        delete:
            remove all folder content
    '''
    serializer_class = FolderSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs['id']
        try:
            folder = Folder.objects.get(id=id)
            shutil.rmtree(MEDIA_ROOT + 'uploads/' + folder.name)
        except Exception:
            print(f'Warning: Local folder id: {id} remove failed! It may be moved.')
        return Folder.objects.filter(id=id)


class SharedFolderDetail(generics.ListAPIView):
    '''
        get:
            View shared files
    '''
    permission_classes =  [permissions.AllowAny] # password required
    lookup_field = 'folder_id'
    serializer_class = FileSerializer

    def get_queryset(self):
        name = self.kwargs['folder_id']
        password = self.request.GET.get("password")
        folder = Folder.objects.filter(name=name,password=password).first()
        return File.objects.filter(folder=folder)


'''File API'''
# passed
class FileCreate(generics.CreateAPIView):
    '''
        post:
            upload file 
    '''
    # a view for listing and creating files
    # lookup_field = 'folder_id'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        folder = self.kwargs['folder_id']
        return File.objects.filter(folder=folder,user=self.request.user)

# passed
class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    '''
        get:
            get file detail
        put:
            update file info
        delete:
            delete/remove file 
    '''
    # a view for retrieving, updating and deleting a file
    lookup_field = 'id'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        file = self.kwargs['id']
        return File.objects.filter(id=file)
    
    def delete(self,request,*args, **kwargs):
        # remove local files
        try:
            file = File.objects.get(id=self.kwargs['id'])
            file_path = file.upload.path
            os.remove(file_path)
            file.delete()
        except FileNotFoundError:
            print(f'Warning: Local file {file.upload.path} remove failed! It may be moved.')
        except ObjectDoesNotExist:
            id = self.kwargs['id']
            print(f'File with id: {id} does not exist!')
        return super().delete(request,*args, **kwargs)
