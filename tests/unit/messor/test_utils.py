from unittest import TestCase
from mock import call, patch, Mock, MagicMock

from messor.utils import ensure_directory, ensure_directories, \
    calculate_checksum, list_directories, list_all_files, \
    stitch_directory_and_files, flatten_list, _calculate_checksum

class TestFlattenList(TestCase):
    def test_flatten_list_flattens_list(self):
        list_to_flatten = [['1', '2'], ['3', '4']]

        ret = flatten_list(list_to_flatten)

        self.assertEqual(ret, ['1', '2', '3', '4'])

class TestStitchDirectoryAndFiles(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()

    def test_stitch_joins_first_and_third_el(self):
        stitch_directory_and_files(('1', '2', ['3', '4']))

        self.assertEqual([call('1', '3'), call('1', '4')], self.os.path.join.mock_calls)

    def test_stitch_returns_list_of_joined(self):
        ret = stitch_directory_and_files(('1', '2', ['3', '4']))

        self.assertEqual(ret, [self.os.path.join.return_value, self.os.path.join.return_value])

class TestListAllFiles(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.flatten_list')
        self.addCleanup(patcher.stop)
        self.flatten = patcher.start()

        patcher = patch('messor.utils.stitch_directory_and_files')
        self.addCleanup(patcher.stop)
        self.stitch = patcher.start()

        patcher = patch('messor.utils.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()

    def test_list_all_files_walks_directory(self):
        list_all_files('/some/path')

        self.os.walk.assert_called_once_with('/some/path')

    def test_list_all_files_stitches_all_files_to_dirs(self):
        self.os.walk.return_value = ['1', '2', '3', '4']

        list_all_files('/some/path')

        self.assertEqual(map(call, self.os.walk.return_value), self.stitch.mock_calls)

    def test_list_all_files_flattens_stitched_lists(self):
        self.os.walk.return_value = ['1']
        list_all_files('/some/path')

        self.flatten.assert_called_once_with([self.stitch.return_value])

    def test_list_all_files_returns_flattened_list(self):
        ret = list_all_files('/some/path')

        self.assertEqual(ret, self.flatten.return_value)

    def test_list_all_files_uses_conn_if_specified(self):
        conn = Mock()
        conn.modules.os.walk.return_value = ['1']

        list_all_files('/some/path', conn)

        conn.modules.os.walk.assert_called_once_with('/some/path')


class TestListDirectories(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.os')
        self.addCleanup(patcher.stop)
        self.os = patcher.start()

    def test_list_directories_lists_dir(self):
        list_directories('/some/path')

        self.os.listdir.assert_called_once_with('/some/path')

    def test_list_directories_filters_directories(self):
        self.os.listdir.return_value = ['dir1', 'file1', 'dir2']
        mock_calls = [
                call('/some/path', 'dir1'),
                call('/some/path', 'file1'),
                call('/some/path', 'dir2'),
        ]

        list_directories('/some/path')

        self.assertEqual(mock_calls, self.os.path.join.mock_calls)
        self.assertEqual(6, len(self.os.path.isdir.mock_calls))

    def test_list_directories_returns_only_directories(self):
        self.os.listdir.return_value = ['dir1', 'dir2']
        self.os.path.isdir.return_value = False

        ret = list_directories('/some/path')

        self.assertEqual([], ret)

    def test_list_directories_uses_conn_if_specified(self):
        conn = Mock()
        conn.modules.os.listdir.return_value = ['dir1', 'file1', 'dir2']

        list_directories('/some/path', conn)

        conn.modules.os.listdir.assert_called_once_with('/some/path')
        self.assertEqual(3, len(conn.modules.os.path.isdir.mock_calls))


class TestCalculateChecksum(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.open')
        self.addCleanup(patcher.stop)
        self.mock_open = patcher.start()

        patcher = patch('messor.utils.hashlib')
        self.addCleanup(patcher.stop)
        self.hlib = patcher.start()

    def test_calculate_checksum_instantiates_hasher(self):
        calculate_checksum('/some/path/file.txt')

        self.hlib.md5.assert_called_once_with()

    def test_calculate_checksum_opens_path_rb(self):
        calculate_checksum('/some/path/file.txt')

        self.mock_open.assert_called_once_with('/some/path/file.txt', 'rb')

    def test_calculate_checksum_reads_bytes_until_empty(self):
        file_handle = self.mock_open.return_value.__enter__.return_value
        file_handle.read.side_effect = ['1', '2', '3', '']
        file_hash = self.hlib.md5.return_value

        calculate_checksum('/some/path/file.txt')

        self.assertEqual(4, len(file_handle.read.mock_calls))

    def test_calculate_checksum_updates_hasher_until_empty(self):
        file_handle = self.mock_open.return_value.__enter__.return_value
        file_handle.read.side_effect = ['1', '2', '3', '']
        file_hash = self.hlib.md5.return_value

        calculate_checksum('/some/path/file.txt')

        self.assertEqual(map(call, ['1', '2', '3']), file_hash.update.mock_calls)

    def test_calculate_checksum_returns_hexdigest(self):
        file_hash = self.hlib.md5.return_value

        ret = calculate_checksum('/some/path/file.txt')

        file_hash.hexdigest.assert_called_once_with()
        self.assertEqual(ret, file_hash.hexdigest.return_value)

    def test_calculate_checksum_uses_conn_if_specified(self):
        conn = MagicMock()

        _calculate_checksum('/some/path/file.txt', conn)

        conn.builtin.open.assert_called_once_with('/some/path/file.txt', 'rb')


class TestEnsureDirectory(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.os.makedirs')
        self.addCleanup(patcher.stop)
        self.makedirs = patcher.start()

        patcher = patch('messor.utils.os.path.exists')
        self.addCleanup(patcher.stop)
        self.exists = patcher.start()

    def test_ensure_directory_mks_dir_if_not_exists(self):
        self.exists.return_value = False

        ensure_directory('dir')

	self.makedirs.assert_called_once_with('dir')

    def test_ensure_directory_not_mks_dir_if_exists(self):
        self.exists.return_value = True

        ensure_directory('dir')

	self.assertEqual(0, len(self.makedirs.mock_calls))

    def test_ensure_directory_uses_conn_if_provided(self):
        conn = Mock()
        conn.modules.os.path.exists.return_value = False

        ensure_directory('dir', conn)

        conn.modules.os.path.exists.assert_called_once_with('dir')
        conn.modules.os.makedirs.assert_called_once_with('dir')


class TestEnsureDirectories(TestCase):
    def setUp(self):
        patcher = patch('messor.utils.ensure_directory')
        self.addCleanup(patcher.stop)
        self.ensure_directory = patcher.start()

    def test_ensure_directories_ensures_all_directories(self):
	ensure_directories(['dir1', 'dir2', 'dir3'])

	mock_calls = self.ensure_directory.mock_calls

	expected_calls = [call('dir1'), call('dir2'), call('dir3')]
	self.assertEqual(expected_calls, mock_calls)
