import os

from messor.utils import list_directories
from messor.settings import FORAGER_BUFFER
from messor.drivers.transfer import FlatBufferDriver
from messor.drivers.reference import ChecksumFilesDriver

reference_driver = ChecksumFilesDriver()
transfer_driver = FlatBufferDriver()

def process_file(file_entry):
    filename, checksum = file_entry
    transfer_driver.ensure_file_in_inbox(filename, checksum)
    reference_file = os.path.join(FORAGER_BUFFER, 'hosts') + filename
    os.remove(reference_file)

def sync_to_inbox(host):
    file_entries = reference_driver.file_index_for_host(host)
    map(process_file, file_entries)

def list_buffer_hosts():
    buffer_path = os.path.join(FORAGER_BUFFER, 'hosts')
    return list_directories(buffer_path)

def drop_off():
    hosts = list_buffer_hosts()
    map(sync_to_inbox, hosts)
