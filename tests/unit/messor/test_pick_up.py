from unittest import TestCase
from mock import patch, call, Mock

from messor.settings import MESSOR_PATH, MESSOR_BUFFER, PICKUP_HOSTS
from messor.pick_up import pick_up, list_outbox_hosts, sync_to_buffer, \
    build_file_index, process_file, create_host_buffer, \
    sync_outbox_host_to_buffer, process_host, list_all_files_for_outbox_host, \
    handle_file, OutOfSpaceError, process_all_files, process_file_group

class TesHandleFile(TestCase):
    def setUp(self):
	patcher = patch('messor.pick_up.os')
	self.addCleanup(patcher.stop)
	self.mock_os = patcher.start()

	patcher = patch('messor.pick_up.ChecksumFilesDriver.ensure_file_in_buffer')
	self.addCleanup(patcher.stop)
	self.ensure_file_in_buffer = patcher.start()

	patcher = patch('messor.pick_up.ChecksumFilesDriver.ensure_filename_reference')
	self.addCleanup(patcher.stop)
	self.ensure_reference = patcher.start()

	self.file_entry = ('/some/absolute/file/path.txt', 'achecksum')
        self.remote_driver = Mock()
	self.remote_driver.file_size.return_value = 1

    def test_handle_file_ensures_file_in_buffer(self):
	handle_file(self.file_entry, self.remote_driver)

	self.ensure_file_in_buffer.assert_called_once_with(self.file_entry[0], self.file_entry[1], self.remote_driver)

    def test_handle_file_ensures_filename_reference(self):
	handle_file(self.file_entry, self.remote_driver)

	self.ensure_reference.assert_called_once_with(*self.file_entry)

    def test_handle_file_removes_synced_file(self):
	handle_file(self.file_entry, self.remote_driver)

        self.remote_driver.remove_file.assert_called_once_with(self.file_entry[0])


class TestProcessFile(TestCase):
    def setUp(self):
	patcher = patch('messor.pick_up.ChecksumFilesDriver.file_fits_in_buffer')
	self.addCleanup(patcher.stop)
	self.file_fits_in_buffer = patcher.start()
        self.file_fits_in_buffer.return_value = True

	patcher = patch('messor.pick_up.handle_file')
	self.addCleanup(patcher.stop)
	self.handle_file = patcher.start()

	self.file_entry = ('/some/absolute/file/path.txt', 'achecksum')
        self.remote_driver = Mock()

    def test_process_file_handles_file_if_filts_in_buffer(self):
	process_file(self.file_entry, self.remote_driver)

        self.handle_file.assert_called_once_with(self.file_entry, self.remote_driver)

    def test_process_file_doesnt_handle_file_if_doesnt_fit_in_buffer(self):
        self.file_fits_in_buffer.return_value = False

	with self.assertRaises(OutOfSpaceError):
	    process_file(self.file_entry, self.remote_driver)


class TestBuildFileIndex(TestCase):
    def setUp(self):
        self.remote_driver = Mock()

    def test_build_file_index_calculates_checksums(self):
	fake_files = ['file1.txt', 'file2.zip']

	build_file_index(fake_files, self.remote_driver)

	self.assertEqual(map(call, fake_files), self.remote_driver.calculate_checksum.mock_calls)

    def test_build_file_index_returns_list_of_files_and_checksums(self):
	fake_files = ['file3.txt', 'file4.zip']
	mock_sums = [Mock(), Mock()]
        self.remote_driver.calculate_checksum.side_effect = mock_sums

	ret = build_file_index(fake_files, self.remote_driver)

	self.assertEqual(zip(fake_files, mock_sums), ret)

class TestListAllFilesOutboxForHost(TestCase):
    def setUp(self):
        self.remote_driver = Mock()

    def test_list_all_files_for_host_lists_all_files(self):
	ret = list_all_files_for_outbox_host('testhost', self.remote_driver)

        self.remote_driver.list_all_files(MESSOR_PATH + '/outbox/' + 'testhost')
        self.assertEqual(ret, self.remote_driver.list_all_files.return_value)


class TestCreateHostBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.pick_up.ensure_directory')
	self.addCleanup(patcher.stop)
	self.ensure = patcher.start()

	patcher = patch('messor.pick_up.os')
	self.addCleanup(patcher.stop)
	self.mock_os = patcher.start()

    def test_create_host_buffer_joins_host_to_buffer_path(self):
        create_host_buffer('testhost')

        self.mock_os.path.join.assert_called_once_with(MESSOR_BUFFER, 'hosts', 'testhost')

    def test_create_host_buffer_creates_host_buffer_directory(self):
        create_host_buffer('testhost')

        self.ensure.assert_called_once_with(self.mock_os.path.join.return_value)

class TestProcessFileGroup(TestCase):
    def setUp(self):
	self.files = Mock()
	self.remote_driver = Mock()

	patcher = patch('messor.pick_up.build_file_index')
	self.addCleanup(patcher.stop)
	self.build_file_index = patcher.start()
	self.file_entries = [Mock(), Mock(), Mock(), Mock(), Mock()]
	self.build_file_index.return_value = self.file_entries

	patcher = patch('messor.pick_up.process_file')
	self.addCleanup(patcher.stop)
	self.process_file = patcher.start()

    def test_process_file_group_builds_file_index(self):
	process_file_group(self.files, self.remote_driver)

	self.build_file_index.assert_called_once_with(self.files, self.remote_driver)

    def test_process_file_group_processes_all_file_entries(self):
	process_file_group(self.files, self.remote_driver)

	expected_calls = [
	    call(self.file_entries[0], self.remote_driver),
	    call(self.file_entries[1], self.remote_driver),
	    call(self.file_entries[2], self.remote_driver),
	    call(self.file_entries[3], self.remote_driver),
	    call(self.file_entries[4], self.remote_driver)
	]
	self.assertEqual(expected_calls, self.process_file.mock_calls)


class TestProcessAllFiles(TestCase):
    def setUp(self):
        self.files = [1, 2, 3, 4, 5]
        self.remote_driver = Mock()

	patcher = patch('messor.pick_up.group_n_elements')
	self.addCleanup(patcher.stop)
	self.group_n_elements = patcher.start()
        self.group_n_elements.return_value = self.files

	patcher = patch('messor.pick_up.process_file_group')
	self.addCleanup(patcher.stop)
	self.process_file_group = patcher.start()

    def test_process_all_files_groups_n_elements(self):
        process_all_files(self.files, self.remote_driver)

        self.group_n_elements.assert_called_once_with(self.files, 20)

    def test_process_all_files_processess_all_files_group(self):
        groups = [[1, 2], [3, 4], [5, 6]]
        self.group_n_elements.return_value = groups

        process_all_files(self.files, self.remote_driver)

        expected_calls = [
	    call(groups[0], self.remote_driver),
	    call(groups[1], self.remote_driver),
	    call(groups[2], self.remote_driver)
        ]
        self.assertEqual(expected_calls, self.process_file_group.mock_calls)


class TestSyncOutboxHostToBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.pick_up.process_file')
	self.addCleanup(patcher.stop)
	self.proccess_file = patcher.start()

	patcher = patch('messor.pick_up.create_host_buffer')
	self.addCleanup(patcher.stop)
	self.create_host_buffer = patcher.start()

	patcher = patch('messor.pick_up.build_file_index')
	self.addCleanup(patcher.stop)
	self.build_file_index = patcher.start()

	patcher = patch('messor.pick_up.list_all_files_for_outbox_host')
	self.addCleanup(patcher.stop)
	self.list_all_files_for_host = patcher.start()
	self.list_all_files_for_host.return_value = [1, 2, 3, 4, 5]

        self.remote_driver = Mock()

    def test_sync_outbox_host_to_buffer_lists_all_files_for_host(self):
        sync_outbox_host_to_buffer('testhost', self.remote_driver)

	self.list_all_files_for_host.assert_called_once_with('testhost', self.remote_driver)

    def test_sync_outbox_host_to_buffer_builds_file_index(self):
        sync_outbox_host_to_buffer('testhost', self.remote_driver)

	self.build_file_index.assert_called_once_with(self.list_all_files_for_host.return_value, self.remote_driver)

    def test_sync_outbox_host_to_buffer_creates_buffer_directory_for_host(self):
        sync_outbox_host_to_buffer('testhost', self.remote_driver)

        self.create_host_buffer.assert_called_once_with('testhost')

    def test_sync_outbox_host_to_buffer_processes_all_files_for_host(self):
	self.build_file_index.return_value = ['file1.txt', 'file2.txt', 'file3.txt']

        sync_outbox_host_to_buffer('testhost', self.remote_driver)

        expected_calls = [
            call('file1.txt', self.remote_driver),
            call('file2.txt', self.remote_driver),
            call('file3.txt', self.remote_driver)
        ]
	self.assertEqual(expected_calls, self.proccess_file.mock_calls)


class TestListOutboxHosts(TestCase):
    def setUp(self):
        self.remote_driver = Mock()

    def test_list_outbox_hosts_returns_list_of_directories(self):
	ret = list_outbox_hosts(self.remote_driver)

        self.remote_driver.list_directories.assert_called_once_with(MESSOR_PATH + '/outbox/')

        self.assertEqual(ret, self.remote_driver.list_directories.return_value)

class TestSyncToBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.pick_up.list_outbox_hosts')
        self.addCleanup(patcher.stop)
        self.list_outbox_hosts = patcher.start()
        self.list_outbox_hosts.return_value = ['host1', 'host2', 'host3']

        patcher = patch('messor.pick_up.sync_outbox_host_to_buffer')
        self.addCleanup(patcher.stop)
        self.sync_outbox_host_to_buffer = patcher.start()

        self.conn = Mock()
        
    def test_sync_to_buffer_lists_outbox_hosts(self):
        sync_to_buffer('testhost', self.conn)

        self.list_outbox_hosts.assert_called_once_with(self.conn)

    def test_sync_to_buffer_syncs_outbox_host_to_buffer_for_all_buffers(self):
        sync_to_buffer('testhost', self.conn)

        expected_calls = [
            call('host1', self.conn),
            call('host2', self.conn),
            call('host3', self.conn)
        ]
        self.assertEqual(expected_calls, self.sync_outbox_host_to_buffer.mock_calls)


class TestProcessHost(TestCase):
    def setUp(self):
        patcher = patch('messor.pick_up.SshDriver')
        self.addCleanup(patcher.stop)
        self.sshdriver = patcher.start()

        patcher = patch('messor.pick_up.sync_to_buffer')
        self.addCleanup(patcher.stop)
        self.sync_to_buffer = patcher.start()

    def test_process_host_instantiates_ssh_driver(self):
        process_host('testhost')

        self.sshdriver.assert_called_once_with('testhost')

    def test_process_host_syncs_to_buffer(self):
        process_host('testhost')

        self.sync_to_buffer.assert_called_once_with('testhost', self.sshdriver.return_value)

    def test_process_host_skips_host_if_can_not_establish_connection(self):
        self.sshdriver.side_effect = EOFError

        process_host('testhost')

        self.assertEqual(0, len(self.sync_to_buffer.mock_calls))


class TestPickup(TestCase):
    def setUp(self):
	patcher = patch('messor.pick_up.list_outbox_hosts')
	self.addCleanup(patcher.stop)
	self.list_outbox_hosts = patcher.start()

	patcher = patch('messor.pick_up.process_host')
	self.addCleanup(patcher.stop)
	self.process_host = patcher.start()

    def test_pick_up_processes_all_hosts(self):
	list_outbox_hosts.return_value = ['host1', 'host2', 'localhost']

        pick_up()

	self.assertEqual(map(call, PICKUP_HOSTS), 
			self.process_host.mock_calls)

