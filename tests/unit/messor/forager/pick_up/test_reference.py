from unittest import TestCase
from mock import patch

from messor.forager.pick_up.reference import ensure_filename_reference, \
    get_reference_driver

@patch('messor.forager.pick_up.reference.ChecksumFilesDriver')
class TestGetReferenceDriver(TestCase):
    def test_get_reference_driver_returns_driver(self, Driver):
	ret = get_reference_driver()

	self.assertEqual(ret, Driver.return_value)

@patch('messor.forager.pick_up.reference.get_reference_driver')
class TestEnsureFilenameReference(TestCase):
    def test_ensure_filename_reference_gets_driver(self, get_driver):
	ensure_filename_reference('afilename', 'achecksum')
	
	get_driver.assert_called_once_with()

    def test_ensure_filename_reference_calls_driver_ensure_reference(self, get_driver):
	ensure = get_driver.return_value.ensure_filename_reference

	ensure_filename_reference('afilename', 'achecksum')

	ensure.assert_called_once_with('afilename', 'achecksum')
