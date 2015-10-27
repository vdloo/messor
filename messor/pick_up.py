import os 
import logging

from messor.settings import MESSOR_PATH, MESSOR_BUFFER, PICKUP_HOSTS
from messor.utils import ensure_directory, group_n_elements
from messor.drivers.reference import ChecksumFilesDriver
from messor.drivers.remote import SshDriver

logger = logging.getLogger(__name__)

reference_driver = ChecksumFilesDriver()

class OutOfSpaceError(RuntimeError):
    pass


def handle_file(file_entry, remote_driver):
    filename, checksum = file_entry
    logger.debug("Processing file %s" % filename)
    reference_driver.ensure_file_in_buffer(filename, checksum, remote_driver)
    reference_driver.ensure_filename_reference(filename, checksum)
    remote_driver.remove_file(filename)

def process_file(file_entry, remote_driver):
    if reference_driver.file_fits_in_buffer(file_entry, remote_driver):
        handle_file(file_entry, remote_driver)
    else:
        logger.debug("File doesn't fit (anymore), skipping: %s" % file_entry[0])
        raise OutOfSpaceError("Buffer too full to process the next file for this host")

def build_file_index(files, remote_driver):
    logger.debug("Building file index")
    checksums = map(remote_driver.calculate_checksum, files)
    return zip(files, checksums)

def create_host_buffer(host):
    logger.debug("Creating host buffer for host %s" % host)
    buffer_path = os.path.join(MESSOR_BUFFER, 'hosts', host)
    ensure_directory(buffer_path)

def list_all_files_for_outbox_host(outbox_host, remote_driver):
    logger.debug("Generating a list of all files for host %s" % outbox_host)
    outbox_host_path = MESSOR_PATH + '/outbox/' + outbox_host
    return remote_driver.list_all_files(outbox_host_path)

def list_outbox_hosts(remote_driver):
    logger.debug("Generating a list of outbox host directories")
    outbox_path = MESSOR_PATH + '/outbox/'
    return remote_driver.list_directories(outbox_path)

def process_file_group(files, remote_driver):
    file_entries = build_file_index(files, remote_driver)
    sorted_file_entries = remote_driver.sort_files_by_size(file_entries)
    map(lambda file_entry: process_file(file_entry, remote_driver), sorted_file_entries)

def process_all_files(files, remote_driver):
    groups = group_n_elements(files, 20)
    map(lambda file_group: process_file_group(file_group, remote_driver), groups)

def sync_outbox_host_to_buffer(outbox_host, remote_driver):
    logger.debug("Syncing host %s to buffer" % outbox_host)
    files = list_all_files_for_outbox_host(outbox_host, remote_driver)
    create_host_buffer(outbox_host)

    try:
        process_all_files(files, remote_driver)
    except OutOfSpaceError:
        logger.debug("Can't fit anything else from host %s" % outbox_host)
    logger.debug("Done syncing host %s" % outbox_host)

def sync_to_buffer(host, remote_driver):
    outbox_hosts = list_outbox_hosts(remote_driver)
    map(lambda outbox_host: sync_outbox_host_to_buffer(outbox_host, remote_driver), outbox_hosts)

def process_host(host):
    try:
	remote_driver = SshDriver(host)
        sync_to_buffer(host, remote_driver)
    except EOFError:
        logger.debug("Host %s not in range (anymore), skipping!" % host)

def pick_up():
    logger.debug("Initiating pickup")
    map(process_host, PICKUP_HOSTS)
    logger.debug("Done syncing all outbox host directories to buffer")
