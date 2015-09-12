from unittest import TestCase
from mock import patch

from messor.drivers.transfer import FlatBufferDriver
from messor.settings import FORAGER_BUFFER

driver = FlatBufferDriver()

@patch('messor.drivers.transfer.calculate_checksum')
@patch('messor.drivers.transfer.copyfile')
@patch('messor.drivers.transfer.os')
class TestEnsureFileInBuffer(TestCase):
    def test_ensure_file_in_buffer_joins_path(self, os, *args):
	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	os.path.join.assert_called_once_with(FORAGER_BUFFER, 'achecksum')

    def test_ensure_file_in_buffer_copies_file_if_dst_doesnt_exist(self, os, copyfile, *_):
	os.path.isfile.return_value = False

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	copyfile.assert_called_once_with('somefile.txt', os.path.join.return_value)

    def test_ensure_file_in_buffer_copies_file_if_exists_but_other_checksum(self, os, copyfile, csum):
	os.path.isfile.return_value = True
	csum.return_value = 'adifferentchecksum'

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	copyfile.assert_called_once_with('somefile.txt', os.path.join.return_value)

    def test_ensure_file_in_buffer_doesnt_copy_file_when_not_necessary(self, os, copyfile, csum):
	os.path.isfile.return_value = True
	csum.return_value = 'achecksum'

	driver.ensure_file_in_buffer('somefile.txt', 'achecksum')

	self.assertEqual(0, len(copyfile.mock_calls))
