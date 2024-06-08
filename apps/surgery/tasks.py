# celery tasks
import os
import cv2
import shutil
import celery
import redis
from EasyShare.celery import app
from celery.signals import worker_ready, worker_shutdown
from django.core.cache import cache
from EasyShare.settings.base import DATA_INFO, FILE_1_POSTFIX, FILE_8_POSTFIX, GPU_DEVICE, OAD_CHECKPOINT, OAD_FILE_OUTPUT_DIR, OAD_OUTPUT_NPY_DIR, OAD_OUTPUT_DIR,\
MAX_EXECUTING_TASK_AT_ONCE, PRE_DUR_FILE_POSTFIX, PRE_FILE_POSTFIX,SEG_FILE_OUTPUT_DIR, SEG_IMG_OUTPUT_DIR, TARGET_DIR, SEG_VIDEO_OUTPUT_DIR,EXTRACT_OUTPUT_DIR
from apps.sharefiles.utils import Django_path_get_path
from .models import Task
from .utils import avi_to_web_mp4, get_free_gpu_memory, Arg, try_reading_video, frames2video
from apps.surgery.libs.seg.surgical_seg_api import SegAPI
from apps.surgery.libs.oad.tools.frames_extraction import extract_frames
from apps.sharefiles.redis_pool import POOL
from apps.surgery.libs.oad.tools.generate_demo_target import generate
from apps.surgery.libs.oad.tools.trans_npy2txt import trans,get_dur_txt
OAD_ENABLE = os.environ.get('OAD_ENABLE')
if OAD_ENABLE == '1':
    from apps.surgery.libs.oad.tools.demo_net import demo
    from apps.surgery.libs.oad.src.utils.parser import load_config
    from apps.surgery.libs.oad.src.config.defaults import assert_and_infer_cfg
from django.db.models import Q
from celery.utils.log import get_task_logger
from apps.surgery.utils import task_success_notification, task_fail_notification

logger = get_task_logger(__name__)

def end_task_meta(task_id):
    '''
        end the task
    '''
    conn = redis.Redis(connection_pool=POOL)
    with conn.lock('task_lock'):
        cache.get("launching_tasks_num", 0)
        running_tasks = cache.get("running_tasks", [])
        if len(running_tasks) > 0 and task_id in running_tasks:
            running_tasks.remove(task_id)
            cache.set("running_tasks", running_tasks)
        if cache.get("launching_tasks_num", 0) > 0:
            cache.decr("launching_tasks_num")

@app.task
def infer_jobs(task_id, video_path, md5):
    '''
        pass video to model to infer
    '''
    conn = redis.Redis(connection_pool=POOL)
    with conn.lock('task_lock'):
        running_num = cache.get("launching_tasks_num", 0)
        already_running = task_id in cache.get("running_tasks", [])
        if already_running:
            logger.info("Task is already running in another worker")
            return
        if running_num >= MAX_EXECUTING_TASK_AT_ONCE:
            logger.info("Reach the max running tasks limit")
            return
        else:
            cache.incr("launching_tasks_num")
            # add to running tasks
            running_tasks = cache.get("running_tasks", [])
            running_tasks.append(task_id)
            cache.set("running_tasks", running_tasks)
    # get task
    task=Task.objects.get(id=task_id)
    logger.info("Infering video: ", video_path)
    task.task_status='executing'
    task.save()
    
    # extract frames
    try:
        logger.info("Extracting frames")
        task.task_status='extracting frames'
        task.task_result_url = ''
        task.save()
        extract_frame_jobs(video_path, md5)
        logger.info("Frames extracted")
    except Exception as e:
        print("Extract frames failed: ", e)
        task.task_status='error'
        task.task_result_url = "Extract frames failed, right-click to retry or try with another video."
        task.save()
        end_task_meta(task_id)
        task_fail_notification(task.user, task)
        return
    # pass to SEG model
    free_mem = get_free_gpu_memory(GPU_DEVICE)
    if free_mem < 5:
        print("GPU memory is not enough")
        task.task_status='pending'
        task.task_result_url = "GPU memory is not enough, waiting for next round"
        task.save()
        end_task_meta(task_id)
        return
    try:
        logger.info("Passing to SEG model")
        task.task_status='SEG inferring'
        task.task_result_url = ''
        task.save()
        seg_jobs_notmpframes(md5)
        logger.info("SEG model done")
    except Exception as e:
        print("SEG model failed: ", e)
        task.task_status='error'
        task.task_result_url = "SEG model failed" 
        task.save()
        end_task_meta(task_id)
        task_fail_notification(task.user, task)
        return
    # pass to OAD model
    # inspect GPU memory usage first
    free_mem = get_free_gpu_memory(GPU_DEVICE)
    if free_mem < 6:
        print("GPU memory is not enough")
        task.task_status='pending'
        task.task_result_url = "GPU memory is not enough, waiting for next round"
        task.save()
        end_task_meta(task_id)
        return
    try:
        logger.info("Passing to OAD model")
        task.task_status='OAD inferring'
        task.task_result_url = ''
        task.save()
        tmp_npy = oad_jobs(video_path,md5)
        logger.info("OAD model done")
    except Exception as e:
        logger.error("OAD model failed: ", e)
        task.task_status='error'
        task.task_result_url = "OAD model failed"
        task.save()
        task_fail_notification(task.user, task)
        end_task_meta(task_id)
        return
    # if the task is done, clear the extracted/processed tmp frames
    # end task
    task.task_status='done'
    task.task_result_url='<a href="file_result?file_id='+str(task.file.id) + '">View Result</a>'
    task.save()
    clean_tmp_data(md5, tmp_npy)
    end_task_meta(task_id)

    task_success_notification(task.user, task)
    return

def clean_tmp_data(md5, tmp_npy):
    try:
        # clean extracted frames
        clean_extracted_frames(md5)
        # clean seg output frames
        clean_seg_tmp_frames(md5)
        # clean oad tmp frames
        os.remove(tmp_npy)
    except Exception as e:
        logger.warning("Clean tmp data failed: ", e)

@app.task
def get_task_n_work():
    '''
        get task from db and start the task
    '''
    # get tasks from db
    tasks=Task.objects.filter(task_status='pending')
    if not tasks:
        logger.info("No pending tasks to do")
        return
    else:
        # get first MAX_EXECUTING_TASK_AT_ONCE tasks to do (sorted by created time)
        tasks = tasks.order_by('task_created_time')
        for task in tasks:
            logger.info(f"Send start signal to task({task.id}): ", task.task_name)
            # start the task
            celery.current_app.send_task('surgery.tasks.infer_jobs',[task.id, Django_path_get_path(task.file),task.file.md5])

def extract_frame_jobs(video_path, md5):
    '''
        extract video frames
    '''
    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    extract_frames(video_dir,video_name,EXTRACT_OUTPUT_DIR,md5,
                24,convert_to_rgb=True,resume=True,single_thread=True,new_height=1080,new_width=1920)
    # output: EXTRACT_OUTPUT_DIR/video_name/{}_{}.jpg

def clean_extracted_frames(md5):
    '''
        clean extracted video frames
    '''
    extracted_output_dir = os.path.join(EXTRACT_OUTPUT_DIR, md5)
    if not os.path.exists(extracted_output_dir):
        logger.warning(f"Extracted frames not found in {extracted_output_dir}")
    # remove dir
    if os.path.isdir(extracted_output_dir):
        shutil.rmtree(extracted_output_dir)

def oad_jobs(video_path,md5):
    '''
        pass video to OAD model
    '''
    # generate npy
    video_name = os.path.basename(video_path).split('.')[0]
    generate(EXTRACT_OUTPUT_DIR, TARGET_DIR, md5)
    pre_file = os.path.join(OAD_FILE_OUTPUT_DIR, md5+PRE_FILE_POSTFIX)
    dur_file = os.path.join(OAD_FILE_OUTPUT_DIR, md5+PRE_DUR_FILE_POSTFIX)
    if os.path.exists(pre_file) and os.path.exists(dur_file):
        print("Done already!")
        return
    # pass to OAD model
    opts = [
        'DATA.DATA_INFO', DATA_INFO,
        'DATA.PATH_TO_DATA_DIR', EXTRACT_OUTPUT_DIR,
        'DATA.VIDEO_FORDER','',
        'DATA.TARGET_FORDER', TARGET_DIR,
        'DEMO.INPUT_VIDEO', [md5],
        'OUTPUT_DIR', OAD_OUTPUT_NPY_DIR,
        'TEST.CHECKPOINT_FILE_PATH', OAD_CHECKPOINT,
        'DEMO.BENCHMARK', False,
    ]
    args = Arg(cfg_files="apps/surgery/libs/oad/configs/Surgery/web.yaml",opts=opts)
    cfg = load_config(args,args.cfg_files)
    cfg = assert_and_infer_cfg(cfg)
    npy_file = demo(cfg=cfg)
    # get from result npy and transform to txt
    trans(npy_file_path=npy_file,txt_file_path=pre_file)
    get_dur_txt(input_file_path=pre_file,output_file_path=dur_file)
    # get duration
    return npy_file

def seg_jobs(md5):
    '''
        pass video to segmentation model
        need to be resumable
    '''
    
    img_dir = os.path.join(EXTRACT_OUTPUT_DIR, md5)
    assert os.path.exists(img_dir), f"{img_dir} not exists"
    img_list = os.listdir(img_dir)
    out_dir = os.path.join(SEG_IMG_OUTPUT_DIR, md5)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(f"Create dir: {out_dir}")
    flags_1_345,flags_8_910 = [],[]    
    num_seg_already_done = len(os.listdir(out_dir))
    if num_seg_already_done > 0:
        print(f"Already done {num_seg_already_done} frames")
    seg = SegAPI()
    # main predicting loop
    for index in range(num_seg_already_done, len(img_list)-1):
        img_path = os.path.join(img_dir, img_list[index])
        assert os.path.exists(img_path)
        img = cv2.imread(img_path)
        assert img is not None
        out_frame, flag_1_345, flag_8_910 = seg.get_vis_flag(img)
        out_path = os.path.join(out_dir, img_list[index])
        cv2.imwrite(out_path, out_frame)
        flags_1_345.append(flag_1_345)
        flags_8_910.append(flag_8_910)
    # destroy the model
    del seg
    # save flags to file
    interact_1_file = os.path.join(SEG_FILE_OUTPUT_DIR, md5+FILE_1_POSTFIX)
    interact_8_file = os.path.join(SEG_FILE_OUTPUT_DIR, md5+FILE_8_POSTFIX)
    if not os.path.exists(SEG_FILE_OUTPUT_DIR):
        os.makedirs(SEG_FILE_OUTPUT_DIR)
    with open(interact_1_file, 'w+') as f:
        f.write("\n".join(flags_1_345))
    with open(interact_8_file, 'w+') as f:
        f.write("\n".join(flags_8_910))
    # save video
    video_out_path = os.path.join(SEG_VIDEO_OUTPUT_DIR, md5+'.mp4')
    if not os.path.exists(SEG_VIDEO_OUTPUT_DIR):
        os.makedirs(SEG_VIDEO_OUTPUT_DIR)

    if not os.path.exists(video_out_path) or not try_reading_video(video_out_path):
        frames2video(md5, out_dir, video_out_path)
    # remove the frames
    for img in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, img))

def clean_seg_tmp_frames(video_path):
    out_dir = os.path.join(SEG_IMG_OUTPUT_DIR, video_path)
    if not os.path.exists(out_dir):
        logger.warning(f"SEG frames not found in {out_dir}")
    # remove dir
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)

def seg_jobs_notmpframes(md5):
    '''
        pass video to segmentation model
        and generate the result video without reading frames from disk
    '''
    img_dir = os.path.join(EXTRACT_OUTPUT_DIR, md5)
    assert os.path.exists(img_dir), f"{img_dir} not exists"
    video_out_path = os.path.join(SEG_VIDEO_OUTPUT_DIR, md5+'.mp4')
    if not os.path.exists(video_out_path) or not try_reading_video(video_out_path):
        if not os.path.exists(SEG_VIDEO_OUTPUT_DIR):
            os.makedirs(SEG_VIDEO_OUTPUT_DIR)
        img_list = os.listdir(img_dir)
        img_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        flags_1_345,flags_8_910 = [],[]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(video_out_path.replace(".mp4",".avi"), fourcc, 24, (1920,1080))
        # main predicting loop
        seg = SegAPI()
        for index in range(len(img_list)-1):
            img_path = os.path.join(img_dir, img_list[index])
            assert os.path.exists(img_path), f"{img_path} not exists"
            img = cv2.imread(img_path)
            assert img is not None, f"{img_path} is not readable"
            out_frame, flag_1_345, flag_8_910 = seg.get_vis_flag(img)
            flags_1_345.append(flag_1_345)
            flags_8_910.append(flag_8_910)
            video_writer.write(out_frame)
        video_writer.release()
        del seg
        # save flags to file
        interact_1_file = os.path.join(SEG_FILE_OUTPUT_DIR, md5+FILE_1_POSTFIX)
        interact_8_file = os.path.join(SEG_FILE_OUTPUT_DIR, md5+FILE_8_POSTFIX)
        if not os.path.exists(SEG_FILE_OUTPUT_DIR):
            os.makedirs(SEG_FILE_OUTPUT_DIR)
        with open(interact_1_file, 'w') as f:
            f.write("\n".join(flags_1_345))
        with open(interact_8_file, 'w') as f:
            f.write("\n".join(flags_8_910))
        # convert to mp4
        avi_to_web_mp4(video_out_path.replace(".mp4",".avi"))
        # remove avi
        os.remove(video_out_path.replace(".mp4",".avi"))
    else:
        print(f"Video {video_out_path} already exists")


@worker_ready.connect
def at_start(sender, **kwargs):
    '''
        start the tasks when worker is ready
        task: infer_jobs 
        data: task in error state
    '''
    logger.info("Worker is ready")
    # get tasks from db
    tasks=Task.objects.filter(Q(task_status='error')
                            # for cold shutdown: 
                            |Q(task_status='doing')
                            |Q(task_status='executing')
                            |Q(task_status='SEG inferring')
                            |Q(task_status='OAD inferring')
                            |Q(task_status='extracting frames')
                            )
    cache.set("launching_tasks_num", 0)
    if not tasks:
        logger.info("No error tasks to retry")
    for task in tasks:
        logger.info("Starting task: ", task.task_name)
        task.task_status='pending'
        task.task_result_url = ''
        task.save()
    cache.set("launching_tasks_num", 0)
    cache.set("running_tasks", [])
    get_task_n_work()

@worker_shutdown.connect
def at_end(sender, **kwargs):
    '''
        end the tasks when worker is ready
        task: infer_jobs 
        data: task in doing state
    '''
    logger.info("Worker is shutting down")
    # get tasks from db
    tasks=Task.objects.filter(task_status='doing')
    cache.set("launching_tasks_num", 0)
    if not tasks:
        logger.info("No doing tasks to end")
        pass
    with sender.app.connection() as conn:
        for task in tasks:
            logger.info("Ending task: ", task.task_name)
            task.task_status='pending'
            task.task_result_url = 'backend shutdown, task is pending again'
            task.save()
