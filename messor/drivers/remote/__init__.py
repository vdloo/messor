import os
import logging
from plumbum import SshMachine
from rpyc.utils.zerodeploy import DeployedServer

from messor.utils import ensure_directory, list_directories, list_all_files, \
    calculate_checksum

logger = logging.getLogger(__name__)

class SshDriver(object):
    def __init__(self, host):
	self.host = host
	self.machine = SshMachine(self.host)
	self.rpyc_serv = DeployedServer(self.machine)
	self.rpyc_conn = self.rpyc_serv.classic_connect()
	self.rpyc_conn.ping()

    def upload(self, local_path, remote_path):
        self.machine.upload(local_path, remote_path)

    def download(self, remote_path, local_path):
        self.machine.download(remote_path, local_path)

    def calculate_checksum(self, filename):
	return calculate_checksum(filename, self.rpyc_conn)

    def isfile(self, filename):
	return self.rpyc_conn.modules.os.path.isfile(filename)

    def ensure_directory(self, path):
	ensure_directory(path, self.rpyc_conn)

    def ensure_parent_directory(self, filename):
	parent_directory = os.path.dirname(filename)
	self.ensure_directory(parent_directory)

    def list_all_files(self, path):
	return list_all_files(path, self.rpyc_conn) 

    def list_directories(self, path):
	return list_directories(path, self.rpyc_conn)

    def remove_file(self, filename):
	self.rpyc_conn.modules.os.remove(filename)

    def file_size(self, filename):
	return self.rpyc_conn.modules.os.path.getsize(filename)

    def sort_file_entries_by_size(self, file_entries):
	return sorted(file_entries, key=lambda file_entry: self.file_size(file_entry[0]))
