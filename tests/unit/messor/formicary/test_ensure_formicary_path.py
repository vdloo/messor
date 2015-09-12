from unittest import TestCase
from mock import patch

from messor.formicary import compose_formicary_path, FORMICARY_PATH

@patch('messor.formicary.os.path')
class TestEnsureFormicaryPath(TestCase):
    def test_ensure_formicary_path_joins_base_with_path(self, path):
        compose_formicary_path('test')
	path.join.assert_called_once_with(FORMICARY_PATH, 'test')

    def test_ensure_formicary_path_returns_joined_path(self, path):
        ret = compose_formicary_path('test')

	self.assertEqual(path.join.return_value, ret)
