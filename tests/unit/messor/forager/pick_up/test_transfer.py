from unittest import TestCase
from mock import patch

from messor.forager.pick_up.transfer import ensure_file_in_buffer

@patch('messor.forager.pick_up.transfer.get_transfer_driver')
class TestEnsureFileInBuffer(TestCase):
    def test_ensure_file_in_buffer_gets_driver(self, get_driver):
	ensure_file_in_buffer('afilename', 'achecksum')
	
	get_driver.assert_called_once_with()

    def test_ensure_file_in_buffer_calls_driver_ensure_file(self, get_driver):
	ensure = get_driver.return_value.ensure_file_in_buffer

	ensure_file_in_buffer('afilename', 'achecksum')

	ensure.assert_called_once_with('afilename', 'achecksum')
