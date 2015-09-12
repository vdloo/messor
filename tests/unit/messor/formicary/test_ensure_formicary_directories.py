from unittest import TestCase
from mock import patch

from messor.formicary import ensure_formicary_directories

@patch('messor.formicary.compose_formicary_path')
@patch('messor.formicary.ensure_directories')
class TestEnsureFormicaryDirectories(TestCase):
    def test_ensure_formicary_directories_composes_dirs(self, ensure, compose):
        ensure_formicary_directories(['dir1', 'dir2'])

	print compose.mock_calls
	self.assertEqual(2, len(compose.mock_calls))

    def test_ensure_formicary_directories_ensures_dirs(self, ensure, compose):
        ensure_formicary_directories(['dir1', 'dir2'])

	ensure.assert_called_once_with(
	    [compose.return_value, compose.return_value]
	)
