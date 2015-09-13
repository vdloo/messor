from unittest import TestCase
from mock import call, patch

from messor.utils import ensure_directory, ensure_directories, \
    calculate_checksum, list_directories, list_all_files, \
    stitch_directory_and_files, flatten_list

class TestFlattenList(TestCase):
    def test_flatten_list_flattens_list(self):
        list_to_flatten = [['1', '2'], ['3', '4']]

        ret = flatten_list(list_to_flatten)

        self.assertEqual(ret, ['1', '2', '3', '4'])

@patch('messor.utils.os')
class TestStitchDirectoryAndFiles(TestCase):
    def test_stitch_joins_first_and_third_el(self, os):
        stitch_directory_and_files(('1', '2', ['3', '4']))

        self.assertEqual([call('1', '3'), call('1', '4')], os.path.join.mock_calls)

    def test_stitch_returns_list_of_joined(self, os):
        ret = stitch_directory_and_files(('1', '2', ['3', '4']))

        self.assertEqual(ret, [os.path.join.return_value, os.path.join.return_value])

@patch('messor.utils.flatten_list')
@patch('messor.utils.stitch_directory_and_files')
@patch('messor.utils.os')
class TestListAllFiles(TestCase):
    def test_list_all_files_walks_directory(self, os, *_):
        list_all_files('/some/path')

        os.walk.assert_called_once_with('/some/path')

    def test_list_all_files_stitches_all_files_to_dirs(self, os, stitch, _):
        os.walk.return_value = ['1', '2', '3', '4']

        list_all_files('/some/path')

        self.assertEqual(map(call, os.walk.return_value), stitch.mock_calls)

    def test_list_all_files_flattens_stitched_lists(self, os, stitch, flatten):
        os.walk.return_value = ['1']
        list_all_files('/some/path')

        flatten.assert_called_once_with([stitch.return_value])

    def teest_list_all_files_returns_flattened_list(self, _1, _2, flatten):
        ret = list_all_files('/some/path')

        self.assertEqual(ret, flatten.return_value)

@patch('messor.utils.os')
class TestListDirectories(TestCase):
    def test_list_directories_lists_dir(self, os):
        list_directories('/some/path')

        os.listdir.assert_called_once_with('/some/path')

    def test_list_directories_filters_directories(self, os):
        os.listdir.return_value = ['dir1', 'file1', 'dir2']

        list_directories('/some/path')

        self.assertEqual(map(call, os.listdir.return_value), os.path.abspath.mock_calls)
        self.assertEqual(6, len(os.path.isdir.mock_calls))

    def test_list_directories_returns_only_directories(self, os):
        os.listdir.return_value = ['dir1', 'dir2']
        os.path.isdir.return_value = False

        ret = list_directories('/some/path')

        self.assertEqual([], ret)

@patch('messor.utils.open')
@patch('messor.utils.hashlib')
class TestCalculateChecksum(TestCase):
    def test_calculate_checksum_instantiates_hasher(self, hlib, _):
        calculate_checksum('/some/path/file.txt')

        hlib.md5.assert_called_once_with()

    def test_calculate_checksum_opens_path_rb(self, _, mock_open):
        calculate_checksum('/some/path/file.txt')

        mock_open.assert_called_once_with('/some/path/file.txt', 'rb')

    def test_calculate_checksum_reads_bytes_until_empty(self, hlib, mock_open):
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.read.side_effect = ['1', '2', '3', '']
        file_hash = hlib.md5.return_value

        calculate_checksum('/some/path/file.txt')

        self.assertEqual(4, len(file_handle.read.mock_calls))

    def test_calculate_checksum_updates_hasher_until_empty(self, hlib, mock_open):
        file_handle = mock_open.return_value.__enter__.return_value
        file_handle.read.side_effect = ['1', '2', '3', '']
        file_hash = hlib.md5.return_value

        calculate_checksum('/some/path/file.txt')

        self.assertEqual(map(call, ['1', '2', '3']), file_hash.update.mock_calls)

    def test_calculate_checksum_returns_hexdigest(self, hlib, _):
        file_hash = hlib.md5.return_value

        ret = calculate_checksum('/some/path/file.txt')

        file_hash.hexdigest.assert_called_once_with()
        self.assertEqual(ret, file_hash.hexdigest.return_value)


@patch('messor.utils.os.makedirs')
@patch('messor.utils.os.path.exists')
class TestEnsureDirectory(TestCase):
    def test_ensure_directory_mks_dir_if_not_exists(self, exists, makedirs):
        exists.return_value = False

        ensure_directory('dir')

	makedirs.assert_called_once_with('dir')

    def test_ensure_directory_not_mks_dir_if_exists(self, exists, makedirs):
        exists.return_value = True

        ensure_directory('dir')

	self.assertEqual(0, len(makedirs.mock_calls))


@patch('messor.utils.ensure_directory')
class TestEnsureDirectories(TestCase):
    def test_ensure_directories_ensures_all_directories(self, ensure_directory):
	ensure_directories(['dir1', 'dir2', 'dir3'])

	mock_calls = ensure_directory.mock_calls

	expected_calls = [call('dir1'), call('dir2'), call('dir3')]
	self.assertEqual(expected_calls, mock_calls)
