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

@patch('messor.drivers.reference.open')
@patch('messor.drivers.reference.ensure_directory')
@patch('messor.drivers.reference.os')
@patch('messor.drivers.reference.ChecksumFilesDriver._reference_path_from_filename')
class TestEnsureFilenameReference(TestCase):
    def test_ensure_filename_reference_gets_reference_path(self, ref_path, *_):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	ref_path.asert_called_once_with('/some/filename.txt')

    def test_ensure_filename_reference_gets_dirname_from_path(self, ref_path, os, *_):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	os.path.dirname.assert_called_once_with(ref_path.return_value)

    def test_ensure_filename_reference_ensures_directory(self, _1, os, ensure_directory, *_):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	ensure_directory.assert_called_once_with(os.path.dirname.return_value)

    def test_ensure_filename_reference_opens_reference_wronly(self, ref_path, _1, _2, mock_open):
	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	mock_open.assert_called_once_with(ref_path.return_value, 'w')
	
    def test_ensure_filename_reference_writes_checksum(self, ref_path, _1, _2, mock_open):
	file_handle = mock_open.return_value.__enter__.return_value

	driver.ensure_filename_reference('/some/filename.txt', 'achecksum')

	file_handle.write.assert_called_once_with('achecksum')
