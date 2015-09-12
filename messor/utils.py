import os
import hashlib
from operator import itemgetter

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def ensure_directories(required_directories):
    return map(ensure_directory, required_directories)

def flatten_list(list_to_flatten):
    return reduce(list.__add__, list_to_flatten, [])

def stitch_directory_and_files(threetuple):
    d, _, fs = threetuple
    return map(lambda f: os.path.join(d, f), fs)

def list_all_files(directory):
    return flatten_list(map(stitch_directory_and_files, os.walk(directory)))

def list_directories(directory):
	filter_directories = lambda host: os.path.isdir(os.path.abspath(host))
	return filter(filter_directories, os.listdir(directory))

def calculate_checksum(path):
    filehash = hashlib.md5() 
    fd = open(path, 'rb')
    buf = fd.read(4096)
    while len(buf) > 0:
	filehash.update(buf)
        buf = fd.read(4096)
    return filehash.hexdigest()
