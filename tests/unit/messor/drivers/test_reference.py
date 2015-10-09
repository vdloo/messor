from unittest import TestCase
from mock import patch

from messor.drivers.reference import ChecksumFilesDriver
from messor.settings import FORMICARY_PATH, FORAGER_BUFFER

driver = ChecksumFilesDriver()

@patch('messor.drivers.reference.os')
class TestReferencePathFromFilename(TestCase):
    def test_reference_path_from_filename_creates_reference(self, os):
	driver._reference_path_from_filename(FORMICARY_PATH + '/outbox/' + 'some/file/name.txt')
	
	os.path.join.assert_called_once_with(FORAGER_BUFFER, "hosts", 'some/file/name.txt')

    def test_reference_path_returns_joined_path(self, os):
	ret = driver._reference_path_from_filename('some/file/name.txt')

	self.assertEqual(os.path.join.return_value, ret)

class TestEnsureFilenameReference(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.open')
        self.addCleanup(patcher.stop)
        self.mock_open = patcher.start()

        patcher = patch('messor.drivers.reference.ensure_directory')
        self.addCleanup(patcher.stop)
        self.ensure_directory = patcher.start()

        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver._reference_path_from_filename')
        self.addCleanup(patcher.stop)
        self.ref_path = patcher.start()

    def test_ensure_filename_reference_gets_reference_path(self):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	self.ref_path.asert_called_once_with('/some/filename.txt')

    def test_ensure_filename_reference_gets_dirname_from_path(self):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	self.mock_os.path.dirname.assert_called_once_with(self.ref_path.return_value)

    def test_ensure_filename_reference_ensures_directory(self):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	self.ensure_directory.assert_called_once_with(self.mock_os.path.dirname.return_value)

    def test_ensure_filename_reference_opens_reference_wronly(self):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	self.mock_open.assert_called_once_with(self.ref_path.return_value, 'w')
	
    def test_ensure_filename_reference_writes_checksum(self):
	file_handle = self.mock_open.return_value.__enter__.return_value

	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	file_handle.write.assert_called_once_with('achecksum')
