from unittest import TestCase
from mock import patch, call

from messor.drivers.transfer import FlatBufferDriver
from messor.settings import FORAGER_BUFFER

class TestPurgFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.transfer.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        self.driver = FlatBufferDriver()

    def test_purge_file_in_buffer_joins_buffer_and_checksum(self):
        self.driver.purge_file_in_buffer('checksum1')

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'checksum1')

    def test_purge_file_in_buffer_removes_file(self):
        self.driver.purge_file_in_buffer('checksum1')
        
        self.mock_os.remove(self.mock_os.path.join.return_value)

class TestPurgeBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.transfer.list_all_files')
        self.addCleanup(patcher.stop)
        self.list_all_files = patcher.start()
        self.list_all_files.return_value = ['1', '2', '3']

        patcher = patch('messor.drivers.transfer.FlatBufferDriver.purge_file_in_buffer')
        self.addCleanup(patcher.stop)
        self.purge_file_in_buffer = patcher.start()

        self.driver = FlatBufferDriver()

    def test_purge_buffer_lists_all_files_in_buffer(self):
        self.driver.purge_buffer(['1', '2', '3'])

        self.list_all_files.assert_called_once_with(FORAGER_BUFFER)

    def test_purge_buffer_purgers_all_files_in_buffer_without_any_unresolved_reference_left(self):
        self.driver.purge_buffer(['2'])

        self.assertEqual(map(call, ['1', '3']), self.purge_file_in_buffer.mock_calls)


class TestEnsureFileInBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.drivers.transfer.os')
	self.addCleanup(patcher.stop)
	self.mock_os = patcher.start()

	patcher = patch('messor.drivers.transfer.copyfile')
	self.addCleanup(patcher.stop)
	self.copyfile = patcher.start()

	patcher = patch('messor.drivers.transfer.calculate_checksum')
	self.addCleanup(patcher.stop)
	self.csum = patcher.start()

        self.driver = FlatBufferDriver()

    def test_ensure_file_in_buffer_joins_path(self):
	self.driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'achecksum')

    def test_ensure_file_in_buffer_copies_file_if_dst_doesnt_exist(self):
	self.mock_os.path.isfile.return_value = False

	self.driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.copyfile.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_copies_file_if_exists_but_other_checksum(self):
	self.mock_os.path.isfile.return_value = True
	self.csum.return_value = 'adifferentchecksum'

	self.driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.copyfile.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_doesnt_copy_file_when_not_necessary(self):
	self.mock_os.path.isfile.return_value = True
	self.csum.return_value = 'achecksum'

	self.driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.assertEqual(0, len(self.copyfile.mock_calls))
