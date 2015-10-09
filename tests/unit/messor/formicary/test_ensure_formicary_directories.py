from unittest import TestCase
from mock import patch

from messor.formicary import ensure_formicary_directories

class TestEnsureFormicaryDirectories(TestCase):
    def setUp(self):
	patcher = patch('messor.formicary.compose_formicary_path')
	self.addCleanup(patcher.stop)
	self.compose = patcher.start()

	patcher = patch('messor.formicary.ensure_directories')
	self.addCleanup(patcher.stop)
	self.ensure = patcher.start()

    def test_ensure_formicary_directories_composes_dirs(self):
        ensure_formicary_directories(['dir1', 'dir2'])

	self.assertEqual(2, len(self.compose.mock_calls))

    def test_ensure_formicary_directories_ensures_dirs(self):
        ensure_formicary_directories(['dir1', 'dir2'])

	self.ensure.assert_called_once_with(
	    [self.compose.return_value, self.compose.return_value]
	)
