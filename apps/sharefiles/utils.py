import os
import hashlib
import uuid

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
    return uuid.uuid4()