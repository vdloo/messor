from unittest import TestCase
from mock import patch, call, Mock

from messor.drivers.remote import SshDriver
class TestSshDriver(TestCase):
    def setUp(self):
	patcher = patch('messor.drivers.remote.SshMachine')
	self.addCleanup(patcher.stop)
	self.sshmachine = patcher.start()

	patcher = patch('messor.drivers.remote.DeployedServer')
	self.addCleanup(patcher.stop)
	self.deployedserver = patcher.start()

	patcher = patch('messor.drivers.remote.calculate_checksum')
	self.addCleanup(patcher.stop)
	self.csum = patcher.start()

        patcher = patch('messor.drivers.remote.ensure_directory')
	self.addCleanup(patcher.stop)
	self.ensure_directory = patcher.start()

        patcher = patch('messor.drivers.remote.list_all_files')
	self.addCleanup(patcher.stop)
	self.list_all_files = patcher.start()

        patcher = patch('messor.drivers.remote.list_all_files')
	self.addCleanup(patcher.stop)
	self.list_all_files = patcher.start()

	self.driver = SshDriver('testhost')

    def test_ssh_driver_init_creates_plumbum_connection(self):
	self.sshmachine.assert_called_once_with('testhost')

    def test_ssh_driver_init_deployes_rpyc_server(self):
	self.deployedserver.assert_called_once_with(
	    self.driver.machine
	)

    def test_ssh_driver_init_gets_rpyc_connection(self):
	self.driver.rpyc_serv.classic_connect.assert_called_once_with()

    def test_ssh_driver_init_pings_rpyc_connection(self):
	self.driver.rpyc_conn.ping.assert_called_once_with()

    def test_ssh_driver_upload_uploads_local_to_remote(self):
	self.driver.upload('local_path', 'remote_path')

	self.driver.machine.upload.assert_called_once_with('local_path', 'remote_path')

    def test_ssh_driver_download_downloads_remote_to_local(self):
	self.driver.download('remote_path', 'local_path')

	self.driver.machine.download.assert_called_once_with('remote_path', 'local_path')

    def test_ssh_driver_calculate_checksum_calculates_checksum(self):
	self.driver.calculate_checksum('filename')

	self.csum.assert_called_once_with('filename', self.driver.rpyc_conn)

    def test_ssh_driver_isfile_checks_if_is_file_on_remote(self):
	ret = self.driver.isfile('filename')

        self.driver.rpyc_conn.modules.os.path.isfile.assert_called_once_with('filename')
        self.assertEqual(ret, self.driver.rpyc_conn.modules.os.path.isfile.return_value)

    def test_ssh_driver_ensure_directory_ensures_directory_on_remote(self):
	self.driver.ensure_directory('mypath')

        self.ensure_directory.assert_called_once_with('mypath', self.driver.rpyc_conn)

    def test_ssh_driver_list_all_files_lists_all_files_on_remote(self):
	ret = self.driver.list_all_files('mypath')

        self.list_all_files.assert_called_once_with('mypath', self.driver.rpyc_conn)
        self.assertEqual(ret, self.list_all_files.return_value)

    def test_ssh_driver_remove_file_removes_file_on_remote(self):
        self.driver.remove_file('filename')

        self.driver.rpyc_conn.modules.os.remove.assert_called_once_with('filename')

    def test_ssh_driver_file_size_calls_getsize_on_remote(self):
	self.driver.file_size('filename')

	self.driver.rpyc_conn.modules.os.path.getsize.assert_called_once_with('filename')

    def test_ssh_driver_file_size_returns_file_size_from_file_on_remote(self):
	ret = self.driver.file_size('filename')

	self.assertEqual(ret, self.driver.rpyc_conn.modules.os.path.getsize.return_value)

    def test_ssh_driver_sort_file_entries_by_size_sorts_file_entries_by_size(self):
        self.driver.file_size = Mock()
	file_entries = [
	    ('file1', 'checksum1'),
	    ('file2', 'checksum2'),
	    ('file3', 'checksum3'),
	]
        self.driver.file_size.side_effect = [2, 3, 1]

	ret = self.driver.sort_file_entries_by_size(file_entries)

	expected_sorted_file_entries = [
	    ('file3', 'checksum3'),
	    ('file1', 'checksum1'),
	    ('file2', 'checksum2'),
	]
	self.assertEqual(expected_sorted_file_entries, ret)

