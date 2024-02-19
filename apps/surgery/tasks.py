# celery tasks
from EasyShare.celery import app

@app.task
def infer_jobs(video_path):
    '''
        pass video to model to infer
    '''
    pass

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
