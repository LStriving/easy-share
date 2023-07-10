import shutil
from rest_framework import generics, permissions,status
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_list_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from apps.access.utils import *
from .models import Folder, File
from django.core.files import File as DJFile
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist

import os


class IsFolderOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the request user has a specific username or email
        folder_id = view.kwargs['folder_id']
        folder = Folder.objects.filter(id=folder_id).first()
        if folder is not None:
            return request.user == folder.user
        return False

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
        return Folder.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FolderUpdate(generics.UpdateAPIView):
    """
        put:
            update folder's name or password
    """
    serializer_class = FolderSerializer
    permission_classes = [IsOwner]
    queryset = Folder.objects.all()

class FolderFiles(generics.ListAPIView):
    '''
        get:
            View files of a folder
    '''
    # a view for viewing folder files by creators using folder_id
    serializer_class = FileSerializer
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
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        id = self.kwargs['id']
        try:
            folder = Folder.objects.get(id=id)
            files = File.objects.filter(folder=folder)
            for file in files:
                os.remove(file.upload.path)
                print(f"Remove:{file.upload.path}")
        except Exception:
            print(f'Warning: Local folder id: {id} remove failed! It may be moved.')
        return Folder.objects.filter(id=id)


class SharedFolderDetail(generics.ListAPIView):
    '''
        get:
            View shared files
    '''
    permission_classes =  [permissions.AllowAny] # password required
    serializer_class = FileSerializer

    def get_queryset(self):
        id = self.kwargs['folder_id']
        name = self.request.GET.get("name")
        password = self.request.GET.get("password")
        folder = Folder.objects.filter(id=id,name=name,password=password).first()
        qset = File.objects.filter(folder=folder)
        return get_list_or_404(qset)

'''File API'''
# passed
class FileCreate(generics.CreateAPIView):
    '''
        post:
            upload file (Return 400 when folder not created)
    '''
    # a view for listing and creating files
    queryset = File.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [IsFolderOwner]
    parser_classes = [MultiPartParser]
    
    def perform_create(self, serializer):
        file = self.request.FILES['upload']
        folder = Folder.objects.get(id=self.kwargs['folder_id'])
        serializer.save(
                    user=self.request.user,
                    folder=folder,
                    upload=file,
                    size=file.size,
                    type=file.content_type,
                    name=file.name)

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
    serializer_class = FileSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        file = self.kwargs['id']
        return File.objects.filter(id=file)
    
    def delete(self,request,*args, **kwargs):
        # remove local files
        try:
            file = File.objects.get(id=self.kwargs['id'])
            self.check_object_permissions(request=request,obj=file)
            file_path = file.upload.path
            os.remove(file_path)
            file.delete()
        except FileNotFoundError:
            print(f'Warning: Local file {file.upload.path} remove failed! It may be moved.')
        except ObjectDoesNotExist:
            id = self.kwargs['id']
            print(f'File with id: {id} does not exist!')
        return Response(status=status.HTTP_204_NO_CONTENT)

'''
Large File upload:
    - 切片上传接口
    - 切片校验，文件合并接口
    - 文件存在验证接口
'''

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def copy_files_to_folder(request,folder_id):
    '''
        post:
            copy uploaded files to a folder by file id list
            content-type: multipart/form-data
    '''
    # check owner
    data = request.POST
    try:
        file_list  = eval(data['file_id_list'])
    except KeyError:
        return Response(data={'message':'Params error'},
                        status=status.HTTP_400_BAD_REQUEST)
    fileset = File.objects.filter(id__in = file_list)
    not_owner_file = []
    for file in fileset:
        if file.user != request.user:
            not_owner_file.append(file.id)
    if len(not_owner_file) != 0:
        return Response(data={'message':f'Permission error with File id: {not_owner_file}'},
                        status=status.HTTP_403_FORBIDDEN)
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return Response(data={'message':'Folder not found, you should create folder \
                            before copy to the destination'},
                        status=status.HTTP_404_NOT_FOUND)
    if folder.user != request.user:
        return Response(data={'message':"You are not the owner of the folder"},
                        status=status.HTTP_403_FORBIDDEN)
    
    # copy files manually
    for src in fileset:
        src_path = src.upload.path
        file_storage_name = os.path.basename(src.upload.path)
        new_dir = os.path.dirname(src.upload.path).replace(src.folder.name, folder.name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        new_file_path = os.path.join(new_dir,file_storage_name)
        try:
            os.link(src_path,new_file_path)
            # create new instance with trick    
            src.upload = new_file_path
            src.folder = folder
            src.pk = None
            src.save()
        except FileExistsError:
            print(f'{new_file_path} have Existed!')
        

    return Response(status=status.HTTP_200_OK)
