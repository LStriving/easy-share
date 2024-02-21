import torch
from torch.types import Device
from typing import Union

def get_free_gpu_memory(device:Union[int, Device]=None):
    '''
        get free gpu memory
    '''
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        free = torch.cuda.mem_get_info(device)[0]
        return free