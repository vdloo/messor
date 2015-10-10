from unittest import TestCase
from mock import patch

from messor.formicary import compose_formicary_path, FORMICARY_PATH

class TestEnsureFormicaryPath(TestCase):
    def setUp(self):
	patcher = patch('messor.formicary.os.path')
	self.addCleanup(patcher.start)
	self.path = patcher.start()

    def test_ensure_formicary_path_joins_base_with_path(self):
        compose_formicary_path('test')
	self.path.join.assert_called_once_with(FORMICARY_PATH, 'test')

    def test_ensure_formicary_path_returns_joined_path(self):
        ret = compose_formicary_path('test')

	self.assertEqual(self.path.join.return_value, ret)
