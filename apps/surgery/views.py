from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions, generics
from rest_framework.response import Response


from access.utils import IsOwner
from sharefiles.utils import Django_path_get_path
from sharefiles.models import File
from .models import Task
from .serializers import TaskSerializer
from .tasks import infer_jobs

# Create your views here.

def index(request):
    return render(request, "index.html")

def monitor(request):
    return render(request, "main.html")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_task(request):
    '''
        add task to queue
    '''
    data = request.POST.get("file_id")
    if not data:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":"File id is required"})
    # get user
    user = request.user
    if not user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error":"User not authenticated"})
    try:
        file = File.objects.get(id=data)
    except File.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error":"File not found"})
    
    if file.user != user or user.is_staff == False:
        return Response(status=status.HTTP_403_FORBIDDEN, data={"error":"Permission denied"})

    task, create = Task.objects.get_or_create(user=user,task_status="pending",file=file)
    task.save()
    if not create:
        return Response(status=status.HTTP_201_CREATED)
    else:
        infer_jobs.delay(Django_path_get_path(file))
        return Response(status=status.HTTP_200_OK)
    

class TaskList(generics.ListAPIView):
    '''
        get task list
    '''
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
