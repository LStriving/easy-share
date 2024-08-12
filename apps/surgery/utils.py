from dataclasses import dataclass
import cv2
import os
import torch
from torch.types import Device
from typing import Union
from EasyShare.settings.base import LOG_DIR
from apps.surgery.libs.seg.surgical_seg_api import SegAPI
from notifications.signals import notify
# from apps.surgery.models import Task


def get_free_gpu_memory(device:Union[int, Device]=None):
    '''
        get free gpu memory
    '''
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        free = torch.cuda.mem_get_info(device)[0] / 1024 / 1024 / 1024 # GB
        return free

@dataclass
class Arg():
    shard_id:int=0
    num_shards:int=1
    init_method:str="tcp://localhost:9999"
    cfg_files:str="configs/Surgery/web.yaml"
    opts:list=None
    

def try_reading_video(video_path):
    #TODO: check the frame count
    '''
        read video and return if it is readable
    '''
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        return True
    except:
        return False

def frames2video(video_name, frames_dir, video_out_path:str):
    print(f"Writing video: {video_name}.avi")
    # read frames and merge to video
    img_list = os.listdir(frames_dir)
    # img name: {}_{index}.jpg
    img_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    img_list = [os.path.join(frames_dir, img) for img in img_list if img.endswith('.jpg')]
    assert os.path.exists(img_list[0]), f"{img_list[0]} not exists"
    img = cv2.imread(img_list[0])
    h,w,c = img.shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(video_out_path.replace(".mp4",".avi"), fourcc, 24, (w,h))
    for img_path in img_list:
        img = cv2.imread(img_path)
        video_writer.write(img)
    video_writer.release()
    print(f"Video {video_name}.avi has been written")
    print(f"Converting {video_name}.avi to {video_name}.mp4")
    avi_to_web_mp4(video_out_path.replace(".mp4",".avi"))
    print(f"Video {video_name}.mp4 has been written, removing {video_name}.avi")
    os.remove(video_out_path.replace(".mp4",".avi"))

def avi_to_web_mp4(input_file_path):
    '''
    ffmpeg -i test_result.avi -vcodec h264 test_result.mp4
    @param: [in] input_file_path 带avi或mp4的非H264编码的视频的全路径
    @return: [output] output_file_path 生成的H264编码视频的全路径
    '''
    assert input_file_path.endswith('.avi'), "input file should be .avi"
    assert os.path.exists(input_file_path), f"{input_file_path} not exists"
    output_file_path = input_file_path[:-3] + 'mp4'
    cmd = 'ffmpeg -y -i {} -vcodec h264 {}'.format(input_file_path, output_file_path)
    # run cmd
    os.system(cmd)
    return output_file_path

def load_model():
    # single instance
    if not hasattr(load_model, "model"):
        load_model.model = SegAPI()
    return load_model.model

def task_success_notification(user, task):
    notify.send(user, recipient=user, verb="Task Success", level="success", public=False,
                description=f"Task {str(task)} has been completed successfully")

def task_fail_notification(user, task):
    notify.send(user, recipient=user, verb="Task Fail", level="error", public=False,
                description=f"Task {str(task)} has failed: {task.task_result_url}")

def write_error_log(error_msg:str, task_id=None, log_dir=LOG_DIR):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, f"{task_id}.log")
    with open(log_path, 'w') as f:
        f.write(f"TASK {task_id}: {error_msg}")

if __name__ == "__main__":
    print(get_free_gpu_memory(0))