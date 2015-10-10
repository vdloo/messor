from unittest import TestCase
from mock import patch

from messor.forager.pick_up.transfer import ensure_file_in_buffer

class TestEnsureFileInBuffer(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.transfer.get_transfer_driver')
	self.addCleanup(patcher.stop)
	self.get_driver = patcher.start()

    def test_ensure_file_in_buffer_gets_driver(self):
	ensure_file_in_buffer('afilename', 'achecksum')
	
	self.get_driver.assert_called_once_with()

    def test_ensure_file_in_buffer_calls_driver_ensure_file(self):
	ensure = self.get_driver.return_value.ensure_file_in_buffer

	ensure_file_in_buffer('afilename', 'achecksum')

	self.ensure.assert_called_once_with('afilename', 'achecksum')
