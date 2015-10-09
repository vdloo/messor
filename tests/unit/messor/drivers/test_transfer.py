from unittest import TestCase
from mock import patch

from messor.drivers.transfer import FlatBufferDriver
from messor.settings import FORAGER_BUFFER

driver = FlatBufferDriver()

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

    def test_ensure_file_in_buffer_joins_path(self):
	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'achecksum')

    def test_ensure_file_in_buffer_copies_file_if_dst_doesnt_exist(self):
	self.mock_os.path.isfile.return_value = False

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.copyfile.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_copies_file_if_exists_but_other_checksum(self):
	self.mock_os.path.isfile.return_value = True
	self.csum.return_value = 'adifferentchecksum'

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.copyfile.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_doesnt_copy_file_when_not_necessary(self):
	self.mock_os.path.isfile.return_value = True
	self.csum.return_value = 'achecksum'

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.assertEqual(0, len(self.copyfile.mock_calls))
