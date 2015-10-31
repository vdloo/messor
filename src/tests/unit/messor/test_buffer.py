from unittest import TestCase
from mock import patch, call, Mock

from messor.buffer import flush_buffer, list_buffer_hosts
from messor.settings import MESSOR_BUFFER

class TestFlushBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.buffer.list_buffer_hosts')
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


class TestListBufferHosts(TestCase):
    def setUp(self):
        patcher = patch('messor.buffer.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        patcher = patch('messor.buffer.list_directories')
        self.addCleanup(patcher.stop)
        self.list_directories = patcher.start()

    def test_list_buffer_hosts_joins_path(self):
        list_buffer_hosts()

        self.mock_os.path.join.assert_called_once_with(MESSOR_BUFFER, 'hosts')

    def test_list_buffer_hosts_lists_directories(self):
        list_buffer_hosts()

        self.list_directories.assert_called_once_with(
            self.mock_os.path.join.return_value
        )

    def test_list_buffer_hosts_returns_list_of_directories(self):
        ret = list_buffer_hosts()

        self.assertEqual(ret, self.list_directories.return_value)

