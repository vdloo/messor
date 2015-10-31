import os
import logging
from itertools import chain

from messor.utils import list_directories
from messor.drivers.reference import ChecksumFilesDriver
from messor.settings import MESSOR_BUFFER

reference_driver = ChecksumFilesDriver()

logger = logging.getLogger(__name__)

def list_buffer_hosts():
    logger.debug("Generating a list of buffer host directories")
    buffer_path = os.path.join(MESSOR_BUFFER, 'hosts')
    return list_directories(buffer_path)

def flush_buffer():
    hosts = list_buffer_hosts()
    zipped_lists = zip(*chain(*map(reference_driver.file_index_for_host, hosts)))
    unresolved_checksums = zipped_lists[1] if zipped_lists else []
    reference_driver.purge_buffer(unresolved_checksums)

