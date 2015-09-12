from unittest import TestCase
from mock import patch

from bin.setup_formicary import main

@patch('bin.setup_formicary.setup_logging')
@patch('bin.setup_formicary.setup_formicary')
class TestSetupFormicary(TestCase):
    def test_main_sets_up_logging(self, setup_formicary, setup_logging):
        main()

        setup_logging.assert_called_once_with()

    def test_main_sets_up_formicary(self, setup_formicary, setup_logging):
        main()

        setup_formicary.assert_called_once_with()
