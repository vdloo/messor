import os 
from operator import itemgetter

from messor.settings import FORMICARY_PATH, FORAGER_BUFFER
from messor.utils import list_all_files, list_directories, calculate_checksum, \
    ensure_directory
from messor.drivers.transfer import FlatBufferDriver
from messor.drivers.reference import ChecksumFilesDriver

reference_driver = ChecksumFilesDriver()
transfer_driver = FlatBufferDriver()

def process_file(file_entry):
    filename, checksum = file_entry
    transfer_driver.ensure_file_in_buffer(filename, checksum)
    reference_driver.ensure_filename_reference(filename, checksum)
    os.remove(filename)

def build_file_index(files):
    checksums = map(calculate_checksum, files)
    return zip(files, checksums)

def list_all_files_for_host(host):
    return list_all_files(FORMICARY_PATH + '/outbox/' + host) 

def create_host_buffer(host):
    buffer_path = os.path.join(FORAGER_BUFFER, 'hosts', host)
    ensure_directory(buffer_path)

def sync_to_buffer(host):
    files = list_all_files_for_host(host)
    file_entries = build_file_index(files)
    create_host_buffer(host)
    map(process_file, file_entries)

def list_outbox_hosts():
    return list_directories(FORMICARY_PATH + '/outbox/')

def pick_up():
    hosts = list_outbox_hosts()
    map(sync_to_buffer, hosts)
