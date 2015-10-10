from unittest import TestCase
from mock import patch

from messor.forager.pick_up.reference import ensure_filename_reference, \
    get_reference_driver

class TestGetReferenceDriver(TestCase):
    @patch('messor.forager.pick_up.reference.ChecksumFilesDriver')
    def test_get_reference_driver_returns_driver(self, Driver):
	ret = get_reference_driver()

	self.assertEqual(ret, Driver.return_value)

class TestEnsureFilenameReference(TestCase):
    def setUp(self):
	patcher = patch('messor.forager.pick_up.reference.get_reference_driver')
	self.addCleanup(patcher.stop)
	self.get_driver = patcher.start()

    def test_ensure_filename_reference_gets_driver(self):
	ensure_filename_reference('afilename', 'achecksum')
	
	self.get_driver.assert_called_once_with()

    def test_ensure_filename_reference_calls_driver_ensure_reference(self):
	ensure = get_driver.return_value.ensure_filename_reference

	ensure_filename_reference('afilename', 'achecksum')

	self.ensure.assert_called_once_with('afilename', 'achecksum')
