import os

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def ensure_directories(required_directories):
    return map(ensure_directory, required_directories)
