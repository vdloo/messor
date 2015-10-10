import os
from shutil import copyfile
from messor.utils import calculate_checksum, ensure_directory
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

# This driver stores the files in a buffer directory using each file's hash as the file name. This means there is deduplication on file level.
class FlatBufferDriver(object):
    def ensure_file_in_buffer(self, filename, checksum):
        dst = os.path.join(FORAGER_BUFFER, checksum)
        if not os.path.isfile(dst) or calculate_checksum(filename) != checksum:
	    copyfile(filename, dst)

    def ensure_file_in_inbox(self, filename, checksum):
        src = os.path.join(FORAGER_BUFFER, checksum)
        dst = FORMICARY_PATH + '/inbox' + filename
        ensure_directory(os.path.dirname(dst))
        if not os.path.isfile(dst) or calculate_checksum(dst) != checksum:
	    copyfile(src, dst)
