import os
import logging
from concurrent.futures import ThreadPoolExecutor

from messor.drivers.reference import ChecksumFilesDriver
from messor.drivers.remote import SshDriver
from messor.buffer import flush_buffer, list_buffer_hosts
from messor.settings import MESSOR_BUFFER

logger = logging.getLogger(__name__)

reference_driver = ChecksumFilesDriver()

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

def drop_off():
    flush_buffer()
    logger.debug("Initiating dropoff")
    hosts = list_buffer_hosts()
    map(process_host, hosts)
