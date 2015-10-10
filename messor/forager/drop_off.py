import os
import logging

from messor.utils import list_directories
from messor.settings import FORAGER_BUFFER
from messor.drivers.transfer import FlatBufferDriver
from messor.drivers.reference import ChecksumFilesDriver

logger = logging.getLogger(__name__)

reference_driver = ChecksumFilesDriver()
transfer_driver = FlatBufferDriver()

def process_file(file_entry):
    filename, checksum = file_entry
    logger.debug("Processing file %s" % filename)
    transfer_driver.ensure_file_in_inbox(filename, checksum)
    reference_file = os.path.join(FORAGER_BUFFER, 'hosts') + filename
    os.remove(reference_file)

def sync_to_inbox(host):
    logger.debug("Syncing host %s to inbox" % host)
    file_entries = reference_driver.file_index_for_host(host)
    map(process_file, file_entries)

def list_buffer_hosts():
    logger.debug("Creating a list of buffer host directories")
    buffer_path = os.path.join(FORAGER_BUFFER, 'hosts')
    return list_directories(buffer_path)

def drop_off():
    logger.debug("Initiating dropoff")
    hosts = list_buffer_hosts()
    map(sync_to_inbox, hosts)
    logger.debug("Done syncing all buffer host directories to inbox")
