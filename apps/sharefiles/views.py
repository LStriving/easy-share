import mimetypes
from rest_framework import generics, permissions,status
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_list_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from EasyShare.settings.base import MAX_HANDLE_FILE
from apps.access.utils import *
from apps.sharefiles.forms import ChunkFileForm
from apps.sharefiles.utils import *
from .models import Folder, File, get_folder_name
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

import os

# TODO: fix or remove
class IsFolderOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the request user has a specific username or email
        # get folder id in different request method by key `folder_id`
        if request.method == 'GET':
            print("GET")
            folder_id = request.GET.get('folder_id')
        else:
            folder_id = view.kwargs.get('folder_id',0)
        print(f"Folder id: {folder_id}")
        folder = Folder.objects.filter(id=folder_id).first()
        if request.user is None:
            print('User not found!')
            return False
        if folder is not None:
            return request.user == folder.user
        return False
    
class IsFolderOwnerOrAdmin(IsFolderOwner):
    def has_permission(self, request, view):
        isAdmin = bool(request.user and request.user.is_staff)
        return super().has_permission(request, view) or isAdmin

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
        # check if the folder name is unique
        name = serializer.validated_data['name']
        print(name)
        if Folder.objects.filter(user=self.request.user,name=name).exists():
            print('Folder name should be unique!')
            return Response(data={'message':'Folder name should be unique!'},
                            status=status.HTTP_201_CREATED)
        print('Creating folder...')
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = self.perform_create(serializer)
        if response is not None:
            return response
        headers = self.get_success_headers(serializer.data)
        print(f"headers:{headers}")
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        
class FolderInfo(generics.RetrieveAPIView):
    '''
        get:
            Return folder info
    '''
    # a view for view folder info

    lookup_field = 'id'
    serializer_class = FolderSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        file = self.kwargs['id']
        return Folder.objects.filter(id=file)

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
            return Folder.objects.filter(id=id)
        except ObjectDoesNotExist:
            print(f'Folder with id: {id} does not exist!')
        except FileNotFoundError as e:
            print(e)
            print(f'Warning: Local folder id: {id} remove failed! Some files may be removed.')


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
        self.request.user.storage += file.size
        self.request.user.save()

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
            md5 = file.md5
            file.delete()
            # remove small file but not large file
            if md5 is None:
                os.remove(file_path)
            else:
                # make link failed
                ...
        except FileNotFoundError:
            print(f'Warning: Local file {file.upload.path} remove failed! It may be moved.')
        except ObjectDoesNotExist:
            id = self.kwargs['id']
            print(f'File with id: {id} does not exist!')
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def copy_files_to_folder(request,folder_id):
    '''
        post:
            copy uploaded files to a folder by file id list
            content-type: multipart/form-data
            ignore duplicate file
    '''
    # data check
    data = request.POST
    try:
        file_list  = eval(data['file_id_list'])
        if not isinstance(file_list,list):
            return Response(data={'message': '"file_id_list" should be a list'}
                            ,status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(data={'message':'Params error'},
                        status=status.HTTP_400_BAD_REQUEST)
    # check owner
    fileset = File.objects.filter(id__in = file_list)
    not_owner_file = []
    for file in fileset:
        if file.user != request.user:
            not_owner_file.append(file.id)
    if len(not_owner_file) != 0:
        return Response(data={'message':f'Permission error with File id: {not_owner_file}'},
                        status=status.HTTP_403_FORBIDDEN)
    if len(file_list) > MAX_HANDLE_FILE:
        return Response(data={'message':f"Too many files at a time, no more than {MAX_HANDLE_FILE}"},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return Response(data={'message':'Folder not found, you should create folder \
                            before copy to the destination'},
                        status=status.HTTP_404_NOT_FOUND)
    if folder.user != request.user:
        return Response(data={'message':"You are not the owner of the folder"},
                        status=status.HTTP_403_FORBIDDEN)
    
    # copy files manually using hardlink
    existed_file_list = []
    for src in fileset:
        src_path = src.upload.path
        file_storage_name = os.path.basename(src.upload.path)
        new_dir = os.path.dirname(src.upload.path).replace(src.folder.name, folder.name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        new_file_path = os.path.join(new_dir,file_storage_name)

        # modify file name when neccessary
        if os.path.exists(new_file_path):
            if not file_same_or_not(src_path,new_file_path):
                new_file_path = os.path.join(new_dir,random_prefix()+file_storage_name)
            else:
                existed_file_list.append(os.path.basename(src.upload.name))
                print(f"File {new_file_path} Existed!")
                continue

        os.link(src_path,new_file_path)
        # create new instance with trick    
        src.upload = new_file_path
        src.folder = folder
        src.pk = None
        src.save()

    if len(existed_file_list) > 0:
        res = ';'.join(existed_file_list)
        return Response(status=status.HTTP_201_CREATED,
                    data={'message':f'{res} have existed!'})

    return Response(status=status.HTTP_200_OK)

'''
Large File upload:
    - [x] 切片上传接口
    - 切片校验，文件合并接口
    - 文件存在验证接口
'''
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def large_file_upload_status(request):
    '''
        get:
            check file upload status(progress)
    '''
    try:
        file_md5 = request.GET['md5']
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'"md5" field is required'})
    try:
        upload_status = get_file_status(file_md5)
    except redis.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                        data={'message':'Redis server not available'})
    if upload_status is None:
        return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'File not uploaded'})
    elif upload_status is True:
        # start to merge if all chunks uploaded
        try:
            folder_id = get_folder_id(file_md5)
        except redis.exceptions.ConnectionError:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                        data={'message':'Redis server not available'})
        try:
            folder_name = Folder.objects.get(id=folder_id).name
        except Folder.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':f'Folder not found (id:{get_folder_id(folder_id)})'})
        # merge_chunks.delay(file_md5,folder_name)
        return Response(status=status.HTTP_200_OK,data={'message':'All chunks uploaded'})
    elif isinstance(upload_status,set):
        return Response(status=status.HTTP_206_PARTIAL_CONTENT,
                        data={'message':f'Index {upload_status} are(is) uploaded.'})
    elif isinstance(upload_status,str):
        return Response(data=upload_status,status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data=f'unknown type:{type(upload_status)}')
    

@api_view(['POST'])
@permission_classes([IsFolderOwnerOrAdmin])
def chunk_file_upload(request,folder_id):
    '''
        post:
            file chunk upload (multipart-formdata)
    '''
    form = ChunkFileForm(request.POST,request.FILES)
    try:
        Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={'message':'folder not found'})
    if form.is_valid():
        md5_value = form.cleaned_data['md5']
        index = form.cleaned_data['index']
        total = form.cleaned_data['total']
        file_name = form.cleaned_data['file_name']
        try:
            set_chunk_meta_cache(md5_value,index,total,file_name,folder_id)
        except redis.exceptions.ConnectionError:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                            data={'message':'Redis server not available'})
        handle_uploaded_chunk(request.FILES["chunk"],md5_value,index)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'message':'check the params'})
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def large_file_instance_create(request,folder_id):
    '''
        post:
            create large file database instance (application/json)
    '''
    # Parse json params
    data = request.data
    user = request.user
    # data = json.loads(data)
    file_md5 = data.get('md5')
    cache.set(f'owner_{file_md5}',user.id)
    if file_md5 is None:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'message':'"md5" field is required in JSON'})
    
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={'message':"folder not found"})
    try:
        file_merged = cache.get(f'{file_md5}_merged')
    except redis.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                        data={'message':'Redis server not available'})
    if file_merged is None:
        return Response(data={'message':f'File chunks not all uploaded or Merged,\
                    you should call /easyshare/large_file_upload_status to check upload status'},
                    status=status.HTTP_303_SEE_OTHER)
    else:
        # check whether the process is truely processing
        if file_merged is False:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                data={'message':f'please wait and send request later'},
                headers={'Retry-After':'60'})
        else:
            res = file_merged
            if isinstance(res,str):
                if not os.path.exists(res):
                    return Response(status=status.HTTP_417_EXPECTATION_FAILED,
                                    data={'message':'Merged file not found, please try to upload it again'})
            # create instance
            file,not_created = File.objects.get_or_create(
                name=os.path.basename(res),
                user=user,
                folder=folder,
                size=os.path.getsize(res),
                defaults={
                    "type":mimetypes.guess_type(res)[0],
                    "md5":file_md5
                }
            )
            file.upload.name = get_folder_name(file,os.path.basename(res))
            file.save()
            if not_created:
                user.storage += file.size
                user.save()
                # cache.delete(f'{file_md5}_merged') # TODO?
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsFolderOwnerOrAdmin])
def merge_upload_chunks(request):
    try:
        file_md5 = request.GET['md5']
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'"md5" field is required'})
    try:
        folder_id = get_folder_id(file_md5)
    except redis.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    data={'message':'Redis server not available'})
    try:
        folder_name = Folder.objects.get(id=folder_id).name
    except Folder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,data={'message':f'Folder not found (id:{get_folder_id(folder_id)})'})
    try:
        upload_status = get_file_status(file_md5)
    except redis.exceptions.ConnectionError:
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE,
                        data={'message':'Redis server not available'})
    if upload_status is str:
        return Response(data=upload_status,status=status.HTTP_200_OK)
    try:
        des = merge_chunks(file_md5,folder_name)
        if des is None:
            return Response(status=status.HTTP_202_ACCEPTED)
        if isinstance(des,str):
            return Response(status=status.HTTP_200_OK,data=des)
        elif isinstance(des,list):
            return Response(status=status.HTTP_206_PARTIAL_CONTENT,data={'message':f'Index {des} are(is) uploaded.'})
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data=str(e))

@api_view(['DELETE','POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_large_file(request):
    '''
        delete:
            remove large file from disk and database forever
        args:
            file_id/md5; folder_id
    '''
    # get args
    data = request.data
    file_id = data.get('file_id')
    if file_id is not None:
        # check file
        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'File not found'})
        if file.md5 is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'Not a large file'})
        # remove file
        try:
            file.delete()
            Django_patch_remove_file(file)
            # remove all cache
            remove_chunk_meta_cache(file.md5)
            # remove file chunks from disk
            remove_chunks(file.md5)
            return Response(status=status.HTTP_200_OK)
        except FileNotFoundError:
            return Response(status=status.HTTP_204_NO_CONTENT,data={'message':'File removed already'})
        except redis.exceptions.ConnectionError:
            pass
    elif file_md5 := data.get('md5'):
        # remove file
        try:
            file = File.objects.get(md5=file_md5)
        except File.DoesNotExist:
            print("File Removed Already, trying to remove chunks")
        if file_md5 is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'Not a large file'})
        try:
            path = cache.get(f'{file_md5}_merged')
            if path is not None:
                os.remove(path=path)
            # remove all cache
            remove_chunk_meta_cache(file_md5)
            # remove file chunks from disk
            remove_chunks(file_md5)
            return Response(status=status.HTTP_200_OK)
        except redis.exceptions.ConnectionError:
            pass
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data=str(e))
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'"file_id" or "md5" field is required'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_filename(request):
    '''
        get:
            check if the file name is existed
    '''
    # get args
    name = request.GET.get('filename')
    folder_id = request.GET.get('folder_id')
    if name is None or folder_id is None:
        return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'"name" and "folder_id" field are required'})
    # check
    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'Folder not found'})
    if File.objects.filter(name=name,folder=folder).exists():
        return Response(status=status.HTTP_200_OK,data={'message':'File name existed'})
    return Response(status=status.HTTP_404_NOT_FOUND,data='OK')

class FileUploadView(TemplateView):
    template_name = 'sharefiles/file_upload.html'

class FolderListWebView(TemplateView):
    template_name = 'sharefiles/folder_list.html'

class FolderDetailView(TemplateView):
    model = Folder
    template_name = 'sharefiles/file_list.html'
    context_object_name = 'folder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['folder_id'] = self.kwargs['folder_id']
        return context