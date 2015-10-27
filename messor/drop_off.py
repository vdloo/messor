import os
import logging
from itertools import chain
from concurrent.futures import ThreadPoolExecutor

from messor.utils import list_directories
from messor.settings import MESSOR_BUFFER
from messor.drivers.reference import ChecksumFilesDriver
from messor.drivers.remote import SshDriver

logger = logging.getLogger(__name__)

reference_driver = ChecksumFilesDriver()

def flush_buffer():
    hosts = list_buffer_hosts()
    zipped_lists = zip(*chain(*map(reference_driver.file_index_for_host, hosts)))
    unresolved_checksums = zipped_lists[1] if zipped_lists else []
    reference_driver.purge_buffer(unresolved_checksums)

def process_file(file_entry, remote_driver):
    filename, checksum = file_entry
    logger.debug("Processing file %s" % filename)
    reference_driver.ensure_file_in_inbox(filename, checksum, remote_driver)
    reference_file = os.path.join(MESSOR_BUFFER, 'hosts') + filename
    os.remove(reference_file)
    flush_buffer()

def sync_to_inbox(host, remote_driver):
    logger.debug("Syncing host %s to inbox" % host)
    file_entries = reference_driver.file_index_for_host(host)
    executor = ThreadPoolExecutor(max_workers=16)
    return list(executor.map(lambda file_entry: process_file(file_entry, remote_driver), file_entries))

def process_host(host):
    try:
	remote_driver = SshDriver(host)
        sync_to_inbox(host, remote_driver)
    except EOFError:
	logger.debug("Host %s not in range, skipping!" % host)

def list_buffer_hosts():
    logger.debug("Generating a list of buffer host directories")
    buffer_path = os.path.join(MESSOR_BUFFER, 'hosts')
    return list_directories(buffer_path)

def drop_off():
    flush_buffer()
    logger.debug("Initiating dropoff")
    hosts = list_buffer_hosts()
    map(process_host, hosts)
