from unittest import TestCase
from mock import patch

from messor.formicary import setup_formicary

class TestMain(TestCase):
    @patch('messor.formicary.ensure_formicary_directories')
    def test_setup_formicary_ensures_formicary_directories(self, ensure_dirs):
	setup_formicary()

	ensure_dirs.asssert_called_once_with(
	    ['outbox', 'inbox']
	)
