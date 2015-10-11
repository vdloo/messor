import os 
import logging
from operator import itemgetter
from rpyc.utils.zerodeploy import DeployedServer
from plumbum import SshMachine

from messor.settings import FORMICARY_PATH, FORAGER_BUFFER, PICKUP_HOSTS
from messor.utils import list_all_files, list_directories, calculate_checksum, \
    ensure_directory
from messor.drivers.reference import ChecksumFilesDriver

logger = logging.getLogger(__name__)

reference_driver = ChecksumFilesDriver()

def process_file(file_entry, conn):
    filename, checksum = file_entry
    logger.debug("Processing file %s" % filename)
    reference_driver.ensure_file_in_buffer(filename, checksum, conn)
    reference_driver.ensure_filename_reference(filename, checksum)
    conn.modules.os.remove(filename)

def build_file_index(files, conn):
    logger.debug("Building file index")
    checksums = map(lambda filename: calculate_checksum(filename, conn), files)
    return zip(files, checksums)

def list_all_files_for_host(host, conn):
    logger.debug("Generating a list of all files for host %s" % host)
    return list_all_files(FORMICARY_PATH + '/outbox/' + host, conn) 

def create_host_buffer(host):
    logger.debug("Creating host buffer for host %s" % host)
    buffer_path = os.path.join(FORAGER_BUFFER, 'hosts', host)
    ensure_directory(buffer_path)

def list_outbox_hosts(conn):
    logger.debug("Generating a list of outbox host directories")
    return list_directories(FORMICARY_PATH + '/outbox/', conn)

def sync_outbox_host_to_buffer(host, conn):
    logger.debug("Syncing host %s to buffer" % host)
    files = list_all_files_for_host(host, conn)
    file_entries = build_file_index(files, conn)
    create_host_buffer(host)
    map(lambda file_entry: process_file(file_entry, conn), file_entries)

def sync_to_buffer(host, conn):
    outbox_hosts = list_outbox_hosts(conn)
    map(lambda host: sync_outbox_host_to_buffer(host, conn), outbox_hosts)

def process_host(host):
    try:
        machine = SshMachine(host)
        server = DeployedServer(machine)
        conn = server.classic_connect()
        conn.ping()
        sync_to_buffer(host, conn)
    except EOFError:
        logger.debug("Host %s not in range, skipping!" % host)

def pick_up():
    logger.debug("Initiating pickup")
    map(process_host, PICKUP_HOSTS)
    logger.debug("Done syncing all outbox host directories to buffer")
