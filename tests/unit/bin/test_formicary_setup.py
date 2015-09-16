from unittest import TestCase
from mock import patch

from bin.formicary_setup import main

@patch('bin.formicary_setup.setup_logging')
@patch('bin.formicary_setup.setup_formicary')
class TestFormicarySetup(TestCase):
    def test_main_sets_up_logging(self, setup_formicary, setup_logging):
        main()

        setup_logging.assert_called_once_with()

    def test_main_sets_up_formicary(self, setup_formicary, setup_logging):
        main()

        setup_formicary.assert_called_once_with()
