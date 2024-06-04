from django.core.management.base import BaseCommand

from sharefiles.utils import get_file_md5
from surgery.tasks import *
from rich import print

class Command(BaseCommand):
    help = 'Run the demo video job, argument: --job=video_job_name --video-path=video_path'

    def handle(self, *args, **options):
        # Run the demo video job
        # get the job name and video path from the options
        job = options['job']
        video_path = options['video_path']
        
        self.check_env(video_path)
        # run the job
        try:
            # get md5
            md5 = get_file_md5(video_path)
            print(f"file MD5: {md5}")
            print(f'extract frames to {EXTRACT_OUTPUT_DIR}/{md5}')
            extract_frame_jobs(video_path, md5)
            print("extract_frame_jobs done, start seg_jobs_notmpframes and oad_jobs...")
            print(f'seg video stores in {SEG_VIDEO_OUTPUT_DIR}/{md5}.mp4')
            seg_jobs_notmpframes(md5)
            print("seg_jobs_notmpframes done, start oad_jobs...")
            oad_jobs(video_path, md5)
            print("oad_jobs done")
            print(f"save to {OAD_FILE_OUTPUT_DIR}")
        except Exception as e:
            self.stdout.write(self.style.ERROR('Error running the demo video job: ' + str(e)))
        self.stdout.write(self.style.SUCCESS('Successfully run the demo video job'))
    
    def check_env(self, video_path):
        # check cuda device
        import torch
        if torch.cuda.is_available():
            # gpu memory
            print(f"cuda memory: {torch.cuda.get_device_properties(0).total_memory}")
        else:
            print("cuda not available, support cuda only for now")
            raise Exception("cuda not available")
        assert os.path.exists(video_path), f"video path {video_path} not exists"
