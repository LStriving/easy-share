from dataclasses import dataclass
import torch
from torch.types import Device
from typing import Union

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
    opts=None
    


if __name__ == "__main__":
    print(get_free_gpu_memory(0))