from unittest import TestCase
from mock import call, patch

from messor.utils import ensure_directory, ensure_directories

#class TestCalculateChecksum(TestCase):
#    def test_calculate_checksum_instantiates_hasher(self, hlib, *_):
#        pass
#
#    def test_calculate_checksum_opens_path(self, *_):
#        pass
#
#    def test_calculate_checksum_reads_bytes_until_empty(self, *_):
#        pass
#
#    def test_calculate_checksum_updates_hasher_until_empty(self, *_):
#	pass
#
#    def test_calculate_checksum_returns_hexdigest(self, *_):
#        pass
#

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
