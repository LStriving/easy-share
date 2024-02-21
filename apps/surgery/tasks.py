# celery tasks
import os
import asyncio

from EasyShare.celery import app
from celery.signals import worker_ready, worker_shutdown
from EasyShare.settings.base import GPU_DEVICE, OAD_OUTPUT_DIR

from apps.sharefiles.utils import Django_path_get_path
from .models import Task
from .utils import get_free_gpu_memory
from apps.surgery.libs.oad.tools.frames_extraction import extract_frames

@app.task
async def infer_jobs(task_id, video_path):
    '''
        pass video to model to infer
    '''
    # get task
    task=Task.objects.get(id=task_id)
    print("Infering video: ", video_path)
    # extract frames
    try:
        print("Extracting frames")
        extract_frame_jobs(video_path)
        print("Frames extracted")
    except Exception as e:
        print("Extract frames failed: ", e)
        task.task_status='error'
        task.save()
        return
    # pass to OAD model
    # inspect GPU memory usage first
    
    free_mem = get_free_gpu_memory(GPU_DEVICE)
    try:
        print("Passing to OAD model")
        oad_jobs(video_path)
        print("OAD model done")
    except Exception as e:
        print("OAD model failed: ", e)
        task.task_status='error'
        task.save()
        return
    
    

def extract_frame_jobs(video_path):
    '''
        extract video frames
    '''
    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    extract_frames(video_dir,video_name,OAD_OUTPUT_DIR,30,convert_to_rgb=True,resume=True)

def oad_jobs(video_path):
    '''
        pass video to OAD model
    '''
    pass

def seg_jobs(video_path):
    '''
        pass video to segmentation model
    '''
    pass

@worker_ready.connect
def at_start(sender, **kwargs):
    '''
        start the tasks when worker is ready
        task: infer_jobs 
        data: task in pending state
    '''
    print("Worker is ready")
    # get tasks from db
    tasks=Task.objects.filter(task_status='pending')
    if not tasks:
        print("No pending tasks to do")
        pass
    with sender.app.connection() as conn:
        for task in tasks:
            print("Starting task: ", task.task_name)
            args=[task.id, Django_path_get_path(task.file)]
            sender.app.send_task('surgery.tasks.infer_jobs', args, connection=conn)
            task.task_status='doing'
            task.save()

@worker_shutdown.connect
def at_end(sender, **kwargs):
    '''
        end the tasks when worker is ready
        task: infer_jobs 
        data: task in doing state
    '''
    print("Worker is shutting down")
    # get tasks from db
    tasks=Task.objects.filter(task_status='doing')
    if not tasks:
        print("No doing tasks to end")
        pass
    with sender.app.connection() as conn:
        for task in tasks:
            print("Ending task: ", task.task_name)
            task.task_status='pending'
            task.save()
    