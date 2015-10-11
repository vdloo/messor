import os
import hashlib
from operator import itemgetter

def flatten_list(list_to_flatten):
    return reduce(list.__add__, list_to_flatten, [])

def stitch_directory_and_files(threetuple):
    d, _, fs = threetuple
    return map(lambda f: os.path.join(d, f), fs)

def list_all_files(directory, conn=None):
    return flatten_list(map(stitch_directory_and_files, 
	    conn.modules.os.walk(directory) if conn else os.walk(directory)))

def list_directories(directory, conn=None):
    os_module = conn.modules.os if conn else os
    filter_directories = lambda dr: os_module.path.isdir(os.path.join(directory, dr))
    return filter(filter_directories, os_module.listdir(directory))

def calculate_checksum(path, conn=None):
    filehash = hashlib.md5() 
    with (conn.builtin.open(path, 'rb') if conn else open(path, 'rb')) as f:
        buf = f.read(4096)
        while len(buf) > 0:
    	    filehash.update(buf)
            buf = f.read(4096)
        return filehash.hexdigest()

def ensure_directory(directory, conn=None):
    if not (conn.modules.os.path.exists(directory) if conn else os.path.exists(directory)):
        conn.modules.os.makedirs(directory) if conn else os.makedirs(directory)

def ensure_directories(required_directories):
    return map(ensure_directory, required_directories)

