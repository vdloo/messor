from unittest import TestCase
from mock import patch, call, Mock
from types import GeneratorType

from messor.drop_off import drop_off, list_buffer_hosts, sync_to_inbox, \
    process_file, process_host
from messor.settings import MESSOR_BUFFER

class TestProcessFile(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.ensure_file_in_inbox')
        self.addCleanup(patcher.stop)
        self.ensure_file_in_inbox = patcher.start()

        patcher = patch('messor.drop_off.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()
        self.mock_os.path.join.return_value = 'hosts_path'

        patcher = patch('messor.drop_off.flush_buffer')
        self.addCleanup(patcher.stop)
        self.flush_buffer = patcher.start()

        self.conn = Mock()

    def test_process_file_ensures_file_in_inbox(self):
        process_file(('filename', 'checksum'), self.conn)

        self.ensure_file_in_inbox.assert_called_once_with('filename', 'checksum', self.conn)

    def test_process_file_creates_composes_file_path(self):
        process_file(('filename', 'checksum'), self.conn)

        self.mock_os.path.join.assert_called_once_with(MESSOR_BUFFER, 'hosts')

    def test_process_file_deletes_reference_file(self):
        process_file(('filename', 'checksum'), self.conn)

        self.mock_os.remove.assert_called_once_with('hosts_path' + 'filename')

    def test_process_file_flushes_inbox(self):
        process_file(('filename', 'checksum'), self.conn)

        self.flush_buffer.assert_called_once_with()


class TestSyncToInbox(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.file_index_for_host')
        self.addCleanup(patcher.stop)
        self.file_index_for_host = patcher.start()

        self.mock_file_entries = [Mock(), Mock(), Mock()]
        self.file_index_for_host.return_value = self.mock_file_entries

        patcher = patch('messor.drop_off.process_file')
        self.addCleanup(patcher.stop)
        self.process_file = patcher.start()

        self.conn = Mock()

    def test_sync_to_inbox_gets_file_index_for_host(self):
        sync_to_inbox('host1', self.conn)

        self.file_index_for_host.assert_called_once_with('host1')

    def test_sync_to_inbox_processes_all_files_for_host(self):
        sync_to_inbox('host1', self.conn)

        expected_calls = [
                call(self.mock_file_entries[0], self.conn),
                call(self.mock_file_entries[1], self.conn),
                call(self.mock_file_entries[2], self.conn),
        ]
        self.assertEqual(expected_calls, self.process_file.mock_calls)

    def test_sync_to_inbox_instantiates_threadpool(self):
        patcher = patch('messor.drop_off.ThreadPoolExecutor')
        self.addCleanup(patcher.stop)
        self.threadpool = patcher.start()

        sync_to_inbox('host1', self.conn)

        self.threadpool.assert_called_once_with(max_workers=16)

    def test_sync_to_inbox_waits_for_threads_to_finish(self):
        ret = sync_to_inbox('host1', self.conn)

        self.assertIsInstance(ret, list)
        self.assertNotIsInstance(ret, GeneratorType)


class TestProcessHost(TestCase):
    def setUp(self):
	patcher = patch('messor.drop_off.SshDriver')
	self.addCleanup(patcher.stop)
	self.sshdriver = patcher.start()

	patcher = patch('messor.drop_off.sync_to_inbox')
	self.addCleanup(patcher.stop)
	self.sync_to_inbox = patcher.start()

    def test_process_host_instantiates_ssh_driver(self):
        process_host('testhost')

        self.sshdriver.assert_called_once_with('testhost')

    def test_process_host_syncs_to_inbox(self):
        process_host('testhost')

        self.sync_to_inbox.assert_called_once_with('testhost', self.sshdriver.return_value)

    def test_process_host_skips_host_if_can_not_establish_connection(self):
        self.sshdriver.side_effect = EOFError

        process_host('testhost')

        self.assertEqual(0, len(self.sync_to_inbox.mock_calls))


class TestDropOff(TestCase):
    def setUp(self):
        patcher = patch('messor.drop_off.flush_buffer')
        self.addCleanup(patcher.stop)
        self.flush_buffer = patcher.start()

        patcher = patch('messor.drop_off.list_buffer_hosts')
        self.addCleanup(patcher.stop)
        self.list_buffer_hosts = patcher.start()
        self.fake_hosts = ['host1', 'host2']
        self.list_buffer_hosts.return_value = self.fake_hosts

        patcher = patch('messor.drop_off.process_host')
        self.addCleanup(patcher.stop)
        self.process_host = patcher.start()

    def test_drop_off_flushes_buffer(self):
        drop_off()

        self.flush_buffer.assert_called_once_with()

    def test_drop_off_lists_buffer_hosts(self):
        drop_off()

        self.list_buffer_hosts.assert_called_once_with()

    def test_drop_off_processes_all_hosts(self):
        drop_off()

        self.assertEqual(map(call, self.fake_hosts), self.process_host.mock_calls)


