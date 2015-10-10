import os
from shutil import copyfile
import logging

from messor.utils import calculate_checksum, ensure_directory
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

logger = logging.getLogger(__name__)

# This driver stores the files in a buffer directory using each file's hash as the file name. This means there is deduplication on file level.
class FlatBufferDriver(object):
    def ensure_file_in_buffer(self, filename, checksum):
	logger.debug("Ensuring file in buffer: %s" % filename)
        dst = os.path.join(FORAGER_BUFFER, checksum)
        if not os.path.isfile(dst) or calculate_checksum(filename) != checksum:
	    logger.debug("Copying file to buffer")
	    copyfile(filename, dst)
	else:
            logger.debug("File already in buffer, skipping!")

    def ensure_file_in_inbox(self, filename, checksum):
	logger.debug("Ensuring file in inbox: %s" % filename)
        src = os.path.join(FORAGER_BUFFER, checksum)
        dst = FORMICARY_PATH + '/inbox' + filename
        ensure_directory(os.path.dirname(dst))
        if not os.path.isfile(dst) or calculate_checksum(dst) != checksum:
	    logger.debug("Copying file to inbox")
	    copyfile(src, dst)
	else:
	    logger.debug("File already in inbox, skipping!")
