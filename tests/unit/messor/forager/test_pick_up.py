from unittest import TestCase
from mock import patch, call

from messor.settings import FORMICARY_PATH, FORAGER_BUFFER
from messor.forager.pick_up import pick_up, list_outbox_hosts, sync_to_buffer, \
    list_all_files_for_host, build_file_index, process_file, create_host_buffer

class TestProcessFile(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.os')
	self.addCleanup(patcher.stop)
	self.mock_os = patcher.start()

	patcher = patch('messor.forager.pick_up.ChecksumFilesDriver.ensure_file_in_buffer')
	self.addCleanup(patcher.stop)
	self.ensure_in_buffer = patcher.start()

	patcher = patch('messor.forager.pick_up.ChecksumFilesDriver.ensure_filename_reference')
	self.addCleanup(patcher.stop)
	self.ensure_reference = patcher.start()

	self.file_entry = ('/some/absolute/file/path.txt', 'achecksum')

    def test_process_file_ensures_file_in_buffer(self):
	process_file(self.file_entry)

	self.ensure_in_buffer.assert_called_once_with(*self.file_entry)

    def test_process_file_ensures_filename_reference(self):
	process_file(self.file_entry)

	self.ensure_reference.assert_called_once_with(*self.file_entry)

    def test_process_file_removes_synced_file(self):
	process_file(self.file_entry)

	self.mock_os.remove.assert_called_once_with(self.file_entry[0])

class TestBuildFileIndex(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.calculate_checksum')
	self.addCleanup(patcher.stop)
	self.calculate_checksum = patcher.start()

    def test_build_file_index_calculates_checksums(self):
	fake_files = ['file1.txt', 'file2.zip']

	build_file_index(fake_files)

	self.assertEqual(map(call, fake_files), self.calculate_checksum.mock_calls)

    def test_build_file_index_returns_list_of_files_and_checksums(self):
	fake_files = ['file3.txt', 'file4.zip']
	mock_sums = [self.calculate_checksum.return_value, self.calculate_checksum.return_value]

	ret = build_file_index(fake_files)

	self.assertEqual(zip(fake_files, mock_sums), ret)

class TestListAllFilesForHost(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.list_all_files')
	self.addCleanup(patcher.stop)
	self.list_all_files = patcher.start()

    def test_list_all_files_for_host_lists_all_files(self):
	ret = list_all_files_for_host('testhost')

	self.list_all_files.assert_called_once_with(FORMICARY_PATH + '/outbox/' + 'testhost')
	self.assertEqual(self.list_all_files.return_value, ret)

class TestCreateHostBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.ensure_directory')
	self.addCleanup(patcher.stop)
	self.ensure = patcher.start()

	patcher = patch('messor.forager.pick_up.os')
	self.addCleanup(patcher.stop)
	self.mock_os = patcher.start()

    def test_create_host_buffer_joins_host_to_buffer_path(self):
        create_host_buffer('testhost')

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'hosts', 'testhost')

    def test_create_host_buffer_creates_host_buffer_directory(self):
        create_host_buffer('testhost')

        self.ensure.assert_called_once_with(self.mock_os.path.join.return_value)

class TestSyncToBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.process_file')
	self.addCleanup(patcher.stop)
	self.proccess_file = patcher.start()

	patcher = patch('messor.forager.pick_up.create_host_buffer')
	self.addCleanup(patcher.stop)
	self.create_host_buffer = patcher.start()

	patcher = patch('messor.forager.pick_up.build_file_index')
	self.addCleanup(patcher.stop)
	self.build_file_index = patcher.start()

	patcher = patch('messor.forager.pick_up.list_all_files_for_host')
	self.addCleanup(patcher.stop)
	self.list_all_files_for_host = patcher.start()

    def test_sync_to_buffer_lists_all_files_for_host(self):
        sync_to_buffer('testhost')

	self.list_all_files_for_host.assert_called_once_with('testhost')

    def test_sync_to_buffer_builds_file_index(self):
        sync_to_buffer('testhost')

	self.build_file_index.assert_called_once_with(self.list_all_files_for_host.return_value)

    def test_sync_to_buffer_creates_buffer_directory_for_host(self):
        sync_to_buffer('testhost')

        self.create_host_buffer.assert_called_once_with('testhost')

    def test_sync_to_buffer_processes_all_files_for_host(self):
	self.build_file_index.return_value = ['file1.txt', 'file2.txt', 'file3.txt']

        sync_to_buffer('testhost')

	self.assertEqual(map(call, self.build_file_index.return_value), self.proccess_file.mock_calls)

class TestListOutboxHosts(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.list_directories')
	self.addCleanup(patcher.stop)
	self.list_dirs = patcher.start()

    def test_list_outbox_hosts_returns_list_of_directories(self):
	ret = list_outbox_hosts()

	self.list_dirs.assert_called_once_with(FORMICARY_PATH + '/outbox/')
	self.assertEqual(ret, self.list_dirs.return_value)


class TestPickup(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.list_outbox_hosts')
	self.addCleanup(patcher.stop)
	self.list_outbox_hosts = patcher.start()

	patcher = patch('messor.forager.pick_up.sync_to_buffer')
	self.addCleanup(patcher.stop)
	self.sync_to_buffer = patcher.start()

    def test_pick_up_lists_outbox_hosts(self):
        pick_up()

	self.list_outbox_hosts.assert_called_once_with()

    def test_pick_up_syncs_all_hosts_to_buffer(self):
	list_outbox_hosts.return_value = ['host1', 'host2', 'localhost']

        pick_up()

	self.assertEqual(map(call, self.list_outbox_hosts.return_value), 
			self.sync_to_buffer.mock_calls)

