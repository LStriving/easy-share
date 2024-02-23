import os
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from EasyShare.settings.base import FILE_1_POSTFIX, FILE_8_POSTFIX, OAD_FILE_OUTPUT_URL,\
PRE_DUR_FILE_POSTFIX, PRE_FILE_POSTFIX, SEG_FILE_OUTPUT_URL, SEG_VIDEO_OUTPUT_URL

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
    task_name = request.POST.get("task_name")
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

    task, create = Task.objects.get_or_create(user=user,file=file,
    defaults={"task_status":"pending", "task_name":task_name, "task_result_url":"In queue"})
    task.save()
    if not create:
        return Response(status=status.HTTP_201_CREATED)
    else:
        infer_jobs.delay(task.id, Django_path_get_path(file))
        return Response(status=status.HTTP_200_OK)
    

class TaskList(generics.ListAPIView):
    '''
        get task list
    '''
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

@login_required(login_url='/')
def task_view(request):
    return render(request, "task.html")

@api_view(['GET'])
def result_view(request):
    # get file id
    file_id = request.GET.get("file_id")
    # check file id
    if not file_id:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":"File id is required"})
    # get file
    try:
        file = File.objects.get(id=file_id)
    except File.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error":"File not found"})
    # todo: check user permission
    # get task
    task = Task.objects.filter(file=file).first()
    if not task:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error":"Task not found"})
    # check task status
    if task.task_status != "done":
        return Response(status=status.HTTP_202_ACCEPTED, data={"error":"Task is not finished yet"})
    # return result
    result_video = os.path.join(SEG_VIDEO_OUTPUT_URL,task.file.name)
    file_345 = os.path.join(SEG_FILE_OUTPUT_URL,task.file.name+FILE_1_POSTFIX)
    file_910 = os.path.join(SEG_FILE_OUTPUT_URL,task.file.name+FILE_8_POSTFIX)
    pred_pro = os.path.join(OAD_FILE_OUTPUT_URL,task.file.name+PRE_FILE_POSTFIX)
    pred_dur = os.path.join(OAD_FILE_OUTPUT_URL,task.file.name+PRE_DUR_FILE_POSTFIX)
    result = {
        "result_video":result_video,
        "file_345": file_345,
        "file_910":file_910,
        "pred_pro": pred_pro,
        "pred_dur": pred_dur
    }
    return render(request, "result.html", result)