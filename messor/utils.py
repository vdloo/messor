import os
import inspect
import string
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
    print 'done listing directories'
    return filter(filter_directories, os_module.listdir(directory))

def _calculate_checksum(path):
    filehash = hashlib.md5() 
    with open(path, 'rb') as f:
        buf = f.read()
        while len(buf) > 0:
            filehash.update(buf)
            buf = f.read(65536)
        return filehash.hexdigest()

def calculate_checksum(path, conn=None):
    if conn:
	conn.execute('import hashlib')
        conn.execute(string.join(inspect.getsourcelines(_calculate_checksum)[0]))
        return conn.namespace['_calculate_checksum'](path)
    else: 
        return _calculate_checksum(path)

def ensure_directory(directory, conn=None):
    if not (conn.modules.os.path.exists(directory) if conn else os.path.exists(directory)):
        conn.modules.os.makedirs(directory) if conn else os.makedirs(directory)

def ensure_directories(required_directories):
    return map(ensure_directory, required_directories)

def path_size(path):
    size = os.path.getsize(path)
    if os.path.isdir(path):
        sub_paths = map(lambda item: os.path.join(path, item), os.listdir(path))
        size += sum(map(path_size, sub_paths))
    return size

def group_n_elements(elements, n=1):
    groups = map(list, zip(*[iter(elements)]*n))
    left = len(elements) % n if n else False
    if left:
        groups.append(elements[-left:])
    return groups
