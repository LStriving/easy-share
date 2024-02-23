# celery tasks
import os
import cv2
import celery
import redis
from EasyShare.celery import app
from celery.signals import worker_ready, worker_shutdown
from django.core.cache import cache
from EasyShare.settings.base import FILE_1_POSTFIX, FILE_8_POSTFIX, GPU_DEVICE, OAD_CHECKPOINT, OAD_FILE_OUTPUT_DIR, OAD_OUTPUT_NPY_DIR, OAD_OUTPUT_DIR,\
MAX_EXECUTING_TASK_AT_ONCE, PRE_DUR_FILE_POSTFIX, PRE_FILE_POSTFIX,SEG_FILE_OUTPUT_DIR, SEG_IMG_OUTPUT_DIR, TARGET_DIR, SEG_VIDEO_OUTPUT_DIR,EXTRACT_OUTPUT_DIR
from apps.sharefiles.utils import Django_path_get_path
from .models import Task
from .utils import get_free_gpu_memory, Arg
from apps.surgery.libs.seg.surgical_seg_api import SegAPI
from apps.surgery.libs.oad.tools.frames_extraction import extract_frames
from apps.sharefiles.redis_pool import POOL
from apps.surgery.libs.oad.tools.generate_demo_target import generate
from apps.surgery.libs.oad.tools.demo_net import demo
from apps.surgery.libs.oad.tools.trans_npy2txt import trans,get_dur_txt
from apps.surgery.libs.oad.src.utils.parser import load_config

def end_task_meta():
    '''
        end the task
    '''
    conn = redis.Redis(connection_pool=POOL)
    with conn.lock('task_lock'):
        cache.decr("launching_tasks_num")

@app.task
def infer_jobs(task_id, video_path):
    '''
        pass video to model to infer
    '''
    # get task
    task=Task.objects.get(id=task_id)
    print("Infering video: ", video_path)
    task.task_status='executing'
    task.save()
    # extract frames
    try:
        print("Extracting frames")
        task.task_status='extracting frames'
        task.task_result_url = ''
        task.save()
        extract_frame_jobs(video_path)
        print("Frames extracted")
    except Exception as e:
        print("Extract frames failed: ", e)
        task.task_status='error'
        task.task_result_url = "Extract frames failed"
        task.save()
        end_task_meta()
        return
    # pass to SEG model
    free_mem = get_free_gpu_memory(GPU_DEVICE)
    if free_mem < 5:
        print("GPU memory is not enough")
        task.task_status='pending'
        task.task_result_url = "GPU memory is not enough, waiting for next round"
        task.save()
        end_task_meta()
        return
    try:
        print("Passing to SEG model")
        task.task_status='SEG inferring'
        task.task_result_url = ''
        task.save()
        seg_jobs(video_path)
        print("SEG model done")
    except Exception as e:
        print("SEG model failed: ", e)
        task.task_status='error'
        task.task_result_url = "SEG model failed" 
        task.save()
        end_task_meta()
        return
    # pass to OAD model
    # inspect GPU memory usage first
    free_mem = get_free_gpu_memory(GPU_DEVICE)
    if free_mem < 10:
        print("GPU memory is not enough")
        task.task_status='pending'
        task.task_result_url = "GPU memory is not enough, waiting for next round"
        task.save()
        end_task_meta()
        return
    try:
        print("Passing to OAD model")
        task.task_status='OAD inferring'
        task.task_result_url = ''
        task.save()
        oad_jobs(video_path)
        print("OAD model done")
    except Exception as e:
        print("OAD model failed: ", e)
        task.task_status='error'
        task.task_result_url = "OAD model failed"
        task.save()
        end_task_meta()
    
    # end task
    task.task_status='done'
    task.task_result_url='file_result?file_id='+str(task.file.id)
    task.save()
    return

@app.task
def get_task_n_work():
    '''
        get task from db and start the task
    '''
    conn = redis.Redis(connection_pool=POOL)
    # get tasks from db
    tasks=Task.objects.filter(task_status='pending')
    if not tasks:
        print("No pending tasks to do")
        return
    else:
        with conn.lock('task_lock'):
            running_num = cache.get("launching_tasks_num", 0)
            if running_num >= MAX_EXECUTING_TASK_AT_ONCE:
                print("Reach the max running tasks limit")
                return
        # get first MAX_EXECUTING_TASK_AT_ONCE tasks to do (sorted by created time)
        tasks = tasks.order_by('task_created_time')[:MAX_EXECUTING_TASK_AT_ONCE-running_num]
        for task in tasks:
            print(f"Starting task({task.id}): ", task.task_name)
            with conn.lock('task_lock'):
                cache.incr("launching_tasks_num")
            # start the task
            celery.current_app.send_task('infer_jobs',[task.id, Django_path_get_path(task.file)])

def extract_frame_jobs(video_path):
    '''
        extract video frames
    '''
    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    extract_frames(video_dir,video_name,EXTRACT_OUTPUT_DIR,24,convert_to_rgb=True,resume=True)
    # output: EXTRACT_OUTPUT_DIR/video_name/{}_{}.jpg

def oad_jobs(video_path):
    '''
        pass video to OAD model
    '''
    # generate npy
    generate(EXTRACT_OUTPUT_DIR, TARGET_DIR)
    video_name = os.path.basename(video_path).split('.')[0]
    # pass to OAD model
    opts = [
        'DATA.PATH_TO_DATA_DIR', EXTRACT_OUTPUT_DIR,
        'DATA.VIDEO_FORDER','',
        'DATA.TARGET_FORDER', TARGET_DIR,
        'DEMO.INPUT_VIDEO', [video_name],
        'DATA.PATH_PREFIX', 'Surgery',
        'OUTPUT_DIR', OAD_OUTPUT_NPY_DIR,
        'TEST.CHECKPOINT_FILE_PATH', OAD_CHECKPOINT,
        'DEMO.BENCHMARK', False,
    ]
    args = Arg(cfg_files="configs/Surgery/web.yaml",opts=opts)
    cfg = load_config(args,args.cfg_files)
    demo(cfg=cfg)
    # get from result npy and transform to txt
    npy_file = os.path.join(OAD_OUTPUT_NPY_DIR, video_name+'.npy')
    pre_file = os.path.join(OAD_FILE_OUTPUT_DIR, video_name+PRE_FILE_POSTFIX)
    dur_file = os.path.join(OAD_FILE_OUTPUT_DIR, video_name+PRE_DUR_FILE_POSTFIX)
    trans(npy_file_path=npy_file,txt_file_path=pre_file)
    get_dur_txt(input_file_path=pre_file,output_file_path=dur_file)
    # get duration

def seg_jobs(video_path):
    '''
        pass video to segmentation model
        need to be resumable
    '''
    seg = SegAPI()
    video_name = os.path.basename(video_path)
    img_dir = os.path.join(OAD_OUTPUT_DIR, video_name)
    assert os.path.exists(img_dir)
    img_list = os.listdir(img_dir)
    out_dir = os.path.join(SEG_IMG_OUTPUT_DIR, video_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    flags_1_345,flags_8_910 = [],[]    
    num_seg_already_done = len(os.listdir(out_dir))
    # main predicting loop
    for index in range(num_seg_already_done, len(img_list)):
        img_path = os.path.join(img_dir, img_list[index])
        out_frame, flag_1_345, flag_8_910 = seg.get_vis_flag(img_path)
        out_path = os.path.join(out_dir, img_list[index])
        cv2.imwrite(out_path, out_frame)
        flags_1_345.append(flag_1_345)
        flags_8_910.append(flag_8_910)
    # destroy the model
    del seg
    # save flags to file
    interact_1_file = os.path.join(SEG_FILE_OUTPUT_DIR, video_name+FILE_1_POSTFIX)
    interact_8_file = os.path.join(SEG_FILE_OUTPUT_DIR, video_name+FILE_8_POSTFIX)
    if not os.path.exists(SEG_FILE_OUTPUT_DIR):
        os.makedirs(SEG_FILE_OUTPUT_DIR)
    with open(interact_1_file, 'w') as f:
        f.write("\n".join(flags_1_345))
    with open(interact_8_file, 'w') as f:
        f.write("\n".join(flags_8_910))
    # save video
    video_out_path = os.path.join(SEG_VIDEO_OUTPUT_DIR, video_name)
    if not os.path.exists(video_out_path):
        os.makedirs(video_out_path)
    # read frames and merge to video
    img_list = os.listdir(out_dir)
    # img name: {}_{index}.jpg
    img_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    img_list = [os.path.join(out_dir, img) for img in img_list]
    img = cv2.imread(img_list[0])
    h,w,c = img.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') #TODO: check whether support for html5
    video_writer = cv2.VideoWriter(os.path.join(video_out_path, video_name), fourcc, 24, (w,h))
    for img in img_list:
        img = cv2.imread(img)
        video_writer.write(img)
    video_writer.release()
    return

@worker_ready.connect
def at_start(sender, **kwargs):
    '''
        start the tasks when worker is ready
        task: infer_jobs 
        data: task in error state
    '''
    print("Worker is ready")
    # get tasks from db
    tasks=Task.objects.filter(task_status='error')
    cache.set("launching_tasks_num", 0)
    if not tasks:
        print("No error tasks to retry")
        
    for task in tasks:
        print("Starting task: ", task.task_name)
        task.task_status='pending'
        task.task_result_url = ''
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
    cache.set("launching_tasks_num", 0)
    if not tasks:
        print("No doing tasks to end")
        pass
    with sender.app.connection() as conn:
        for task in tasks:
            print("Ending task: ", task.task_name)
            task.task_status='pending'
            task.task_result_url = 'backend shutdown, task is pending again'
            task.save()