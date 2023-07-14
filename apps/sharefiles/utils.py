import os
import hashlib
import uuid
import glob
from django.core.cache import cache
from EasyShare.celery import app
from EasyShare.settings.base import MEDIA_ROOT

# TODO: needs to check
def file_same_or_not(path1,path2):
    s1 = os.path.getsize(path1)
    s2 = os.path.getsize(path2)
    if s1 != s2:
        return False
    hash1 = hashlib.md5() # create a hash object
    hash2 = hashlib.md5() # create another hash object
    with open(path1, "rb") as f: # open the first file in binary mode
        for chunk in iter(lambda: f.read(4096), b""): # read the file in chunks
            hash1.update(chunk) # update the hash value with each chunk
    with open(path2, "rb") as f: # open the second file in binary mode
        for chunk in iter(lambda: f.read(4096), b""): # read the file in chunks
            hash2.update(chunk) # update the hash value with each chunk
    if hash1.hexdigest() != hash2.hexdigest(): # compare the hex digest of the hash values
        return False
    
    return True

def random_prefix():
    return str(uuid.uuid4()) + '_'

'''
Cache:
    - <md5, total>
    - <md5_uploaded, uploaded_list>
    - <file_name_md5,file_name>
    - <folder_id_md5,folder_id>
    - <md5_merged, destination>
'''

def get_file_status(md5):
    '''
        Return:
            - None: not uploaded
            - str: file path, uploaded/merged 
            - set: uploading
            - True: uploaded but not merged yet
    '''
    total = cache.get(md5)
    if total is None:
        des = cache.get(f'{md5}_merged')
        if des is not None:
            return des
        return None
    else:
        uploaded = cache.get(f"{md5}_uploaded")
        if len(uploaded) == total:
            return True
    return uploaded

def get_folder_id(md5):
    return cache.get(f'folder_id_{md5}')

def set_chunk_meta_cache(md5_value,index,total,file_name,folder_id):
    if cache.get(md5_value) is None:
        cache.set(md5_value,total)
        cache.set(f'{md5_value}_uploaded',set([index]))
        cache.set(f'file_name_{md5_value}',file_name)
        cache.set(f'folder_id_{md5_value}',folder_id)
    else:
        indices = cache.get(f'{md5_value}_uploaded')
        indices.add(index)
        cache.set(f'{md5_value}_uploaded',indices)

def get_file_md5(filename):
    '''
    return lower case md5 value
    '''
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def handle_uploaded_chunk(f,md5,index):
    path = os.path.join(MEDIA_ROOT,'tmp',md5, str(index))
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def split_file_into_chunks(filename, chunk_size):
    chunk_index = 0
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk, chunk_index
            chunk_index += 1


@app.task
def merge_chunks(md5,folder_name):
    # get locked:
    res = cache.get(f'{md5}_merged')
    if res is False:
        return 'Task launched in other place, skip...'
    elif isinstance(res,str):
        return res 
    cache.set(f'{md5}_merged',False)

    # start the job
    filename = cache.get(f'file_name_{md5}')
    chunks_dir = os.path.join(MEDIA_ROOT,'tmp',md5)
    chunk_file_path = os.listdir(chunks_dir)
    total = cache.get(md5)
    if len(chunk_file_path) != total:
        missing_chunk_index = [i for i in range(1,total+1) if str(i) not in chunk_file_path]
        cache.delete(f'{md5}_merged')
        return missing_chunk_index
    else:
        try:
            chunk_file_path = [os.path.join(chunks_dir,i) for i in chunk_file_path]
            # start to merge
            destination = os.path.join(MEDIA_ROOT,'uploads',
                            folder_name,filename)
            if os.path.exists(destination):
                destination = os.path.join(MEDIA_ROOT,'uploads',
                            folder_name,random_prefix()+filename)
            des_dir = os.path.dirname(destination)
            if not os.path.exists(des_dir):
                os.makedirs(des_dir)
            with open(destination,'wb')as out:
                for chunk in sorted((chunk_file_path)):
                    with open(chunk,'rb')as f:
                        content = f.read()
                        out.write(content)
                    os.remove(chunk)
            os.rmdir(chunks_dir)
            cache.delete_many([f'file_name_{md5}',f'folder_id_{md5}',f'{md5}_uploaded',md5])
            if md5 != get_file_md5(destination):
                cache.delete(f'{md5}_merged')
                os.remove(destination)
                return None
            cache.set(f'{md5}_merged',destination)
            return destination
        except Exception as e:
            print(e)
            cache.delete(f'{md5}_merged')
