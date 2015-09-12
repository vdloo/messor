import os
from shutil import copyfile
from messor.utils import calculate_checksum
from messor.settings import FORAGER_BUFFER

# This driver stores the files in a buffer directory using each file's hash as the file name. This means there is deduplication on file level.
class FlatBufferDriver(object):
    def ensure_file_in_buffer(self, filename, checksum):
        dst = os.path.join(FORAGER_BUFFER, checksum)
        if not os.path.isfile(dst) or calculate_checksum(filename) != checksum:
	    copyfile(filename, dst)
