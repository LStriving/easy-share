from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Folder, File
from .serializers import FolderSerializer, FileSerializer, SharedFolderSerializer

# Create your views here.
'''Folder API'''
class FolderList(generics.ListCreateAPIView):
    # a view for view user's created folders & creating folders
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Folder.objects.filter(creator=self.request.user)

class FolderFiles(generics.RetrieveUpdateDestroyAPIView):
    # a view for retrieving, updating and deleting a folder by creator
    # queryset = Folder.objects.all()
    serializer_class = FileSerializer
    lookup_field = 'folder_id'
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        folder = self.kwargs['folder_id']
        return File.objects.filter(user=self.request.user, folder=folder)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class SharedFolderDetail(generics.RetrieveAPIView):
    permission_classes =  [permissions.AllowAny] # password required
    serializer_class = FileSerializer
    def get_queryset(self):
        name = self.request.GET.get("folder_name")
        password = self.request.GET.get("password")
        folder = Folder.objects.filter(name=name,password=password)
        return File.objects.filter(folder=folder)

'''File API'''
class FileList(generics.ListAPIView):
    # a view for listing and creating files
    # lookup_field = 'folder_id'
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        folder = self.kwargs['folder_id']
        return File.objects.filter(folder=folder)
    
class FileCreate(generics.CreateAPIView):
    # a view for listing and creating files
    # lookup_field = 'folder_id'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        folder = self.kwargs['folder_id']
        return File.objects.filter(folder=folder,user=self.request.user)

class FileDetail(generics.RetrieveUpdateDestroyAPIView):
    # a view for retrieving, updating and deleting a file
    lookup_field = 'file_id'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        file = self.kwargs['file_id']
        return File.objects.filter(file=file)