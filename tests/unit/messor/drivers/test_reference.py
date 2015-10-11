from unittest import TestCase
from mock import patch, call, Mock

from messor.drivers.reference import ChecksumFilesDriver
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

driver = ChecksumFilesDriver()

class TestPurgeFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

    def test_purge_file_in_buffer_joins_buffer_and_checksum(self):
        driver.purge_file_in_buffer('checksum1')

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'checksum1')

    def test_purge_file_in_buffer_removes_file(self):
        driver.purge_file_in_buffer('checksum1')
        
        self.mock_os.remove(self.mock_os.path.join.return_value)

class TestPurgeBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.list_all_files')
        self.addCleanup(patcher.stop)
        self.list_all_files = patcher.start()
        self.list_all_files.return_value = ['1', '2', '3']

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.purge_file_in_buffer')
        self.addCleanup(patcher.stop)
        self.purge_file_in_buffer = patcher.start()

    def test_purge_buffer_lists_all_files_in_buffer(self):
        driver.purge_buffer(['1', '2', '3'])

        self.list_all_files.assert_called_once_with(FORAGER_BUFFER)

    def test_purge_buffer_purgers_all_files_in_buffer_without_any_unresolved_reference_left(self):
        driver.purge_buffer(['2'])

        self.assertEqual(map(call, ['1', '3']), self.purge_file_in_buffer.mock_calls)


class TestEnsureFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        patcher = patch('messor.drivers.reference.copyfileobj')
        self.addCleanup(patcher.stop)
        self.copyfileobj = patcher.start()

        patcher = patch('messor.drivers.reference.calculate_checksum')
        self.addCleanup(patcher.stop)
        self.csum = patcher.start()

        patcher = patch('messor.drivers.reference.open')
        self.addCleanup(patcher.stop)
        self.mock_open = patcher.start()

        self.conn = Mock()

    def test_ensure_file_in_buffer_joins_path(self):
        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.mock_os.path.join.assert_called_once_with(FORAGER_BUFFER, 'achecksum')

    def test_ensure_file_in_buffer_opens_source_file(self):
        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.conn.builtin.open.assert_called_once_with('somefile.txt')

    def test_ensure_file_in_buffer_opens_destination_file(self):
        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.mock_open.assert_called_once_with(self.mock_os.path.join.return_value, 'w')

    def test_ensure_file_in_buffer_copies_file_if_dst_doesnt_exist(self):
        self.mock_os.path.isfile.return_value = False

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.copyfileobj.assert_called_once_with(
            self.conn.builtin.open.return_value,
            self.mock_open.return_value
        )

    def test_ensure_file_in_buffer_copies_file_if_exists_but_other_checksum(self):
        self.mock_os.path.isfile.return_value = True
        self.csum.return_value = 'adifferentchecksum'

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.copyfileobj.assert_called_once_with(
            self.conn.builtin.open.return_value,
            self.mock_open.return_value
        )

    def test_ensure_file_in_buffer_doesnt_copy_file_when_not_necessary(self):
        self.mock_os.path.isfile.return_value = True
        self.csum.return_value = 'achecksum'

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.conn)

        self.assertEqual(0, len(self.copyfileobj.mock_calls))


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
