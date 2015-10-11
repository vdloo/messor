from unittest import TestCase
from mock import patch, call, Mock

from messor.settings import FORAGER_BUFFER
from messor.forager.drop_off import drop_off, list_buffer_hosts, sync_to_inbox, \
    flush_buffer, process_file

class TestProcessFile(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.ensure_file_in_inbox')
        self.addCleanup(patcher.stop)
        self.ensure_file_in_inbox = patcher.start()

        patcher = patch('messor.forager.drop_off.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()
        self.mock_os.path.join.return_value = 'hosts_path'

    def test_process_file_ensures_file_in_inbox(self):
        process_file(('filename', 'checksum'))

        self.ensure_file_in_inbox.assert_called_once_with('filename', 'checksum')

    def test_process_file_creates_composes_file_path(self):
        process_file(('filename', 'checksum'))

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'hosts')

    def test_process_file_deletes_reference_file(self):
        process_file(('filename', 'checksum'))

        self.mock_os.remove.assert_called_once_with('hosts_path' + 'filename')


class TestFlushBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.forager.drop_off.list_buffer_hosts')
        self.addCleanup(patcher.stop)
        self.list_buffer_hosts = patcher.start()
        self.fake_hosts = ['host1', 'host2', 'host3']
        self.list_buffer_hosts.return_value = self.fake_hosts

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.file_index_for_host')
        self.addCleanup(patcher.stop)
        self.file_index_for_host = patcher.start()
        self.file_index_for_host.side_effect = [
            [('filename1', 'checksum1')],
            [('filename2', 'checksum2')],
            [('filename3', 'checksum3')]
        ]

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.purge_buffer')
        self.addCleanup(patcher.stop)
        self.purge_buffer = patcher.start()

    def test_flush_buffer_lists_buffer_hosts(self):
        flush_buffer()

        self.list_buffer_hosts.assert_called_once_with()

    def test_flush_buffer_gets_file_index_for_each_host(self):
        flush_buffer()
        
        self.assertEqual(map(call, self.fake_hosts), self.file_index_for_host.mock_calls)

    def test_flush_buffer_purges_buffer_with_all_found_checksums(self):
        flush_buffer()

        self.assertEqual(
            call(('checksum1', 'checksum2', 'checksum3')),
            self.purge_buffer.call_args
        )

class TestSyncToInbox(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.file_index_for_host')
        self.addCleanup(patcher.stop)
        self.file_index_for_host = patcher.start()

        self.mock_file_entries = [Mock(), Mock(), Mock()]
        self.file_index_for_host.return_value = self.mock_file_entries

        patcher = patch('messor.forager.drop_off.process_file')
        self.addCleanup(patcher.stop)
        self.process_file = patcher.start()

        patcher = patch('messor.forager.drop_off.flush_buffer')
        self.addCleanup(patcher.stop)
        self.flush_buffer = patcher.start()

    def test_sync_to_inbox_gets_file_index_for_host(self):
        sync_to_inbox('host1')

        self.file_index_for_host.assert_called_once_with('host1')

    def test_sync_to_inbox_processes_all_files_for_host(self):
        sync_to_inbox('host1')

        self.assertEqual(map(call, self.mock_file_entries), self.process_file.mock_calls)

    def test_sync_to_inbox_flushes_buffer(self):
        sync_to_inbox('host1')

        self.flush_buffer.assert_called_once_with()


class TestListBufferHosts(TestCase):
    def setUp(self):
        patcher = patch('messor.forager.drop_off.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        patcher = patch('messor.forager.drop_off.list_directories')
        self.addCleanup(patcher.stop)
        self.list_directories = patcher.start()

    def test_list_buffer_hosts_joins_path(self):
        list_buffer_hosts()

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'hosts')

    def test_list_buffer_hosts_lists_directories(self):
        list_buffer_hosts()

        self.list_directories.assert_called_once_with(
            self.mock_os.path.join.return_value
        )

    def test_list_buffer_hosts_returns_list_of_directories(self):
        ret = list_buffer_hosts()

        self.assertEqual(ret, self.list_directories.return_value)


class TestDropOff(TestCase):
    def setUp(self):
        patcher = patch('messor.forager.drop_off.list_buffer_hosts')
        self.addCleanup(patcher.stop)
        self.list_buffer_hosts = patcher.start()
        self.fake_hosts = ['host1', 'host2']
        self.list_buffer_hosts.return_value = self.fake_hosts

        patcher = patch('messor.forager.drop_off.sync_to_inbox')
        self.addCleanup(patcher.stop)
        self.sync_to_inbox = patcher.start()

    def test_drop_off_lists_buffer_hosts(self):
        drop_off()

        self.list_buffer_hosts.assert_called_once_with()

    def test_drop_off_syncs_all_buffer_hosts_to_inbox(self):
        drop_off()

        self.assertEqual(map(call, self.fake_hosts), self.sync_to_inbox.mock_calls)


