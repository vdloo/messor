from unittest import TestCase
from mock import patch, call, Mock

from messor.drivers.reference import ChecksumFilesDriver
from messor.settings import MESSOR_BUFFER, MESSOR_PATH, LIMIT_IN_BYTES

driver = ChecksumFilesDriver()

class TestPurgeFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

    def test_purge_file_in_buffer_joins_buffer_and_checksum(self):
        driver.purge_file_in_buffer('checksum1')

        self.mock_os.path.join.assert_called_once_with(MESSOR_BUFFER, 'checksum1')

    def test_purge_file_in_buffer_removes_file(self):
        driver.purge_file_in_buffer('checksum1')
        
        self.mock_os.remove(self.mock_os.path.join.return_value)

    def test_purge_file_in_buffer_doesnt_remove_directory(self):
        self.mock_os.path.isdir.return_value = True

        driver.purge_file_in_buffer('checksum1')

        self.assertEqual(0, len(self.mock_os.remove.mock_calls))


class TestEnoughSpace(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.path_size')
        self.addCleanup(patcher.stop)
        self.path_size = patcher.start()
        self.path_size.return_value = 9

        self.remote_driver = Mock()
        self.remote_driver.file_size.return_value = 1

    def test_enough_space_gets_path_size_of_buffer(self):
        driver.enough_space(('filename', 'achecksum'), self.remote_driver)

        self.path_size.assert_called_once_with(MESSOR_BUFFER)

    def test_enough_space_gets_remote_file_size(self):
        driver.enough_space(('filename', 'achecksum'), self.remote_driver)

        self.remote_driver.file_size.assert_called_once_with('filename')

    def test_enough_space_left_returns_false_if_not_enough_space_left(self):
        self.remote_driver.file_size.return_value = LIMIT_IN_BYTES

        ret = driver.enough_space(('filename', 'achecksum'), self.remote_driver)

        self.assertFalse(ret)

    def test_enough_space_left_returns_true_if_enough_space_left(self):
        self.remote_driver.file_size.return_value = LIMIT_IN_BYTES - 10

        ret = driver.enough_space(('filename', 'achecksum'), self.remote_driver)

        self.assertTrue(ret)
        

class TestFileFitsInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.file_in_buffer')
        self.addCleanup(patcher.stop)
        self.file_in_buffer = patcher.start()

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.enough_space')
        self.addCleanup(patcher.stop)
        self.enough_space = patcher.start()

        self.remote_driver = Mock()

    def test_file_fits_in_buffer_is_true_if_file_in_buffer_already(self):
        self.file_in_buffer.return_value = True
        self.enough_space.return_value = False

        ret = driver.file_fits_in_buffer(('filename', 'achecksum'), self.remote_driver)

        self.assertTrue(ret)

    def test_file_fits_in_buffer_is_true_if_file_not_in_buffer_but_enough_space(self):
        self.file_in_buffer.return_value = False
        self.enough_space.return_value = True

        ret = driver.file_fits_in_buffer(('filename', 'achecksum'), self.remote_driver)

        self.assertTrue(ret)

    def test_file_fits_in_buffer_is_false_if_not_in_buffer_already_and_not_enough_space(self):
        self.file_in_buffer.return_value = False
        self.enough_space.return_value = False

        ret = driver.file_fits_in_buffer(('filename', 'achecksum'), self.remote_driver)

        self.assertFalse(ret)

    def test_file_fits_in_buffer_calls_file_in_buffer_with_right_parameters(self):
        driver.file_fits_in_buffer(('filename', 'achecksum'), self.remote_driver)

        self.file_in_buffer.assert_called_once_with('filename', 'achecksum')

    def test_file_fits_in_buffer_calls_enough_space_with_right_parameters(self):
        self.file_in_buffer.return_value = False

        driver.file_fits_in_buffer(('filename', 'achecksum'), self.remote_driver)

        self.enough_space.assert_called_once_with(('filename', 'achecksum'), self.remote_driver)

class TestFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()
    
        patcher = patch('messor.drivers.reference.calculate_checksum')
        self.addCleanup(patcher.stop)
        self.calculate_checksum = patcher.start()
    
    def test_file_in_buffer_joins_path(self):
        driver.file_in_buffer('filename', 'achecksum')

        self.os.path.join.assert_called_once_with(MESSOR_BUFFER, 'achecksum')

    def test_file_in_buffer_is_true_if_is_file_and_checksum_matches(self):
        self.os.path.isfile.return_value = True
        self.calculate_checksum.return_value = 'achecksum'

        ret = driver.file_in_buffer('filename', 'achecksum')

        self.assertTrue(ret)

    def test_file_in_buffer_is_false_if_not_file_but_checksum_matches(self):
        self.os.path.isfile.return_value = False
        self.calculate_checksum.return_value = 'achecksum'

        ret = driver.file_in_buffer('filename', 'achecksum')

        self.assertFalse(ret)

    def test_file_in_buffer_is_false_if_is_file_but_checksum_does_not_match(self):
        self.os.path.isfile.return_value = True
        self.calculate_checksum.return_value = 'someotherchecksum'

        ret = driver.file_in_buffer('filename', 'achecksum')

        self.assertFalse(ret)

    def test_file_in_buffer_calls_isfile_with_dst(self):
        driver.file_in_buffer('filename', 'achecksum')

        self.os.path.isfile.assert_called_once_with(self.os.path.join.return_value)

    def test_file_in_buffer_compares_checksum_of_right_file(self):
        driver.file_in_buffer('filename', 'achecksum')

        self.calculate_checksum.assert_called_once_with(self.os.path.join.return_value)


class TestPurgeBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()
        self.os.listdir.return_value = ['1', '2', '3']

        patcher = patch('messor.drivers.reference.ChecksumFilesDriver.purge_file_in_buffer')
        self.addCleanup(patcher.stop)
        self.purge_file_in_buffer = patcher.start()

    def test_purge_buffer_lists_all_files_in_buffer(self):
        driver.purge_buffer(['1', '2', '3'])

        self.os.listdir.assert_called_once_with(MESSOR_BUFFER)

    def test_purge_buffer_purgers_all_files_in_buffer_without_any_unresolved_reference_left(self):
        driver.purge_buffer(['2'])

        self.assertEqual(map(call, ['1', '3']), self.purge_file_in_buffer.mock_calls)


class TestEnsureFileInBuffer(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.mock_os = patcher.start()

        patcher = patch('messor.drivers.reference.calculate_checksum')
        self.addCleanup(patcher.stop)
        self.csum = patcher.start()

        self.remote_driver = Mock()

    def test_ensure_file_in_buffer_joins_path(self):
        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.remote_driver)

        self.mock_os.path.join.has_calls(
                call(MESSOR_BUFFER, 'achecksum'),
                call(MESSOR_BUFFER, 'achecksum')
        )

    def test_ensure_file_in_buffer_copies_file_if_dst_doesnt_exist(self):
        self.mock_os.path.isfile.return_value = False

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.remote_driver)

        self.remote_driver.download.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_copies_file_if_exists_but_other_checksum(self):
        self.mock_os.path.isfile.return_value = True
        self.csum.return_value = 'adifferentchecksum'

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.remote_driver)

        self.remote_driver.download.assert_called_once_with('somefile.txt', self.mock_os.path.join.return_value)

    def test_ensure_file_in_buffer_doesnt_copy_file_when_not_necessary(self):
        self.mock_os.path.isfile.return_value = True
        self.csum.return_value = 'achecksum'

        driver.ensure_file_in_buffer('somefile.txt', 'achecksum', self.remote_driver)

        self.assertEqual(0, len(self.remote_driver.download.mock_calls))


class TestEnsureFileInInbox(TestCase):
    def setUp(self):
        patcher = patch('messor.drivers.reference.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()
        self.src = self.os.path.join.return_value
        self.dst = MESSOR_PATH + '/inbox' + 'filename'

        self.remote_driver = Mock()
        self.remote_driver.isfile.return_value = False
        self.remote_driver.calculate_checksum.return_value = 'someotherchecksum'

    def test_ensure_file_in_inbox_joins_path(self):
        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.os.path.join.assert_called_once_with(MESSOR_BUFFER, 'achecksum')

    def test_ensure_file_in_inbox_ensures_parent_directory(self):
        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.remote_driver.ensure_parent_directory_assert_called_once_with(self.src)

    def test_ensure_file_in_inbox_checks_if_dst_isfile(self):
        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.remote_driver.isfile.assert_called_once_with(self.dst)

    def test_ensure_file_in_inbox_calculates_checksum_of_dst_if_file_already_exists(self):
        self.remote_driver.isfile.return_value = True

        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.remote_driver.calculate_checksum.assert_called_once_with(self.dst)

    def test_ensure_file_in_inbox_uploads_file_if_does_not_exists(self):
        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.remote_driver.upload.assert_called_once_with(self.src, self.dst)

    def test_ensure_file_in_inbox_doesnt_upload_file_if_checksum_matches(self):
        self.remote_driver.isfile.return_value = True
        self.remote_driver.calculate_checksum.return_value = 'achecksum'

        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)

        self.assertEqual(0, len(self.remote_driver.upload.mock_calls))

    def test_ensure_file_in_inbox_uploads_file_if_not_exists_and_checksum_does_not_match(self):
        self.remote_driver.calculate_checksum.return_value = 'achecksum'

        driver.ensure_file_in_inbox('filename', 'achecksum', self.remote_driver)
        
        self.remote_driver.upload.assert_called_once_with(self.src, self.dst)


@patch('messor.drivers.reference.os')
class TestReferencePathFromFilename(TestCase):
    def test_reference_path_from_filename_creates_reference(self, os):
	driver._reference_path_from_filename(MESSOR_PATH + '/outbox/' + 'some/file/name.txt')
	
	os.path.join.assert_called_once_with(MESSOR_BUFFER, "hosts", 'some/file/name.txt')

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
