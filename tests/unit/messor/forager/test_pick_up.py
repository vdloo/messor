from unittest import TestCase
from mock import patch, call

from messor.settings import FORMICARY_PATH, FORAGER_BUFFER
from messor.forager.pick_up import pick_up, list_outbox_hosts, sync_to_buffer, \
    list_all_files_for_host, build_file_index, process_file, create_host_buffer

@patch('messor.forager.pick_up.os')
@patch('messor.forager.pick_up.ChecksumFilesDriver.ensure_filename_reference')
@patch('messor.forager.pick_up.FlatBufferDriver.ensure_file_in_buffer')
class TestProcessFile(TestCase):
    file_entry = ('/some/absolute/file/path.txt', 'achecksum')

    def test_process_file_ensures_file_in_buffer(self, ensure_in_buffer, _, *args):
	process_file(self.file_entry)

	ensure_in_buffer.assert_called_once_with(*self.file_entry)

    def test_process_file_ensures_filename_reference(self, _, ensure_reference, *args):
	process_file(self.file_entry)

	ensure_reference.assert_called_once_with(*self.file_entry)

    def test_process_file_removes_synced_file(self, _1, _2, os):
	process_file(self.file_entry)

	os.remove.assert_called_once_with(self.file_entry[0])

@patch('messor.forager.pick_up.calculate_checksum')
class TestBuildFileIndex(TestCase):
    def test_build_file_index_calculates_checksums(self, calculate_checksum):
	fake_files = ['file1.txt', 'file2.zip']

	build_file_index(fake_files)

	self.assertEqual(map(call, fake_files), calculate_checksum.mock_calls)

    def test_build_file_index_returns_list_of_files_and_checksums(self, calculate_checksum):
	fake_files = ['file3.txt', 'file4.zip']
	mock_sums = [calculate_checksum.return_value, calculate_checksum.return_value]

	ret = build_file_index(fake_files)

	self.assertEqual(zip(fake_files, mock_sums), ret)

@patch('messor.forager.pick_up.list_all_files')
class TestListAllFilesForHost(TestCase):
    def test_list_all_files_for_host_lists_all_files(self, laf):
	ret = list_all_files_for_host('testhost')

	laf.assert_called_once_with(FORMICARY_PATH + '/outbox/' + 'testhost')
	self.assertEqual(laf.return_value, ret)

@patch('messor.forager.pick_up.ensure_directory')
@patch('messor.forager.pick_up.os')
class TestCreateHostBuffer(TestCase):
    def test_create_host_buffer_joins_host_to_buffer_path(self, os, *_):
        create_host_buffer('testhost')

        os.path.join.assert_called_once_with(FORAGER_BUFFER, 'hosts', 'testhost')

    def test_create_host_buffer_creates_host_buffer_directory(self, os, ensure):
        create_host_buffer('testhost')

        ensure.assert_called_once_with(os.path.join.return_value)

@patch('messor.forager.pick_up.process_file')
@patch('messor.forager.pick_up.create_host_buffer')
@patch('messor.forager.pick_up.build_file_index')
@patch('messor.forager.pick_up.list_all_files_for_host')
class TestSyncToBuffer(TestCase):
    def test_sync_to_buffer_lists_all_files_for_host(self, laf_for_host, *args):
        sync_to_buffer('testhost')

	laf_for_host.assert_called_once_with('testhost')

    def test_sync_to_buffer_builds_file_index(self, laf_for_host, build_fi, *args):
        sync_to_buffer('testhost')

	build_fi.assert_called_once_with(laf_for_host.return_value)

    def test_sync_to_buffer_creates_buffer_directory_for_host(self, _1, _2, create_host_buffer, *args):
        sync_to_buffer('testhost')

        create_host_buffer.assert_called_once_with('testhost')

    def test_sync_to_buffer_processes_all_files_for_host(self, _1, build_fi, _2, pf, *args):
	build_fi.return_value = ['file1.txt', 'file2.txt', 'file3.txt']

        sync_to_buffer('testhost')

	self.assertEqual(map(call, build_fi.return_value), pf.mock_calls)

@patch('messor.forager.pick_up.list_directories')
class TestListOutboxHosts(TestCase):
    def test_list_outbox_hosts_returns_list_of_directories(self, list_dirs):
	ret = list_outbox_hosts()

	list_dirs.assert_called_once_with(FORMICARY_PATH + '/outbox/')
	self.assertEqual(ret, list_dirs.return_value)


@patch('messor.forager.pick_up.list_outbox_hosts')
@patch('messor.forager.pick_up.sync_to_buffer')
class TestPickup(TestCase):
    def test_pick_up_lists_outbox_hosts(self, _, list_outbox_hosts):
        pick_up()

	list_outbox_hosts.assert_called_once_with()

    def test_pick_up_syncs_all_hosts_to_buffer(self, sync_to_buffer, 
		    list_outbox_hosts):
	list_outbox_hosts.return_value = ['host1', 'host2', 'localhost']

        pick_up()

	self.assertEqual(map(call, list_outbox_hosts.return_value), 
			sync_to_buffer.mock_calls)

