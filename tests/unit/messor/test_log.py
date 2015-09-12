from unittest import TestCase
from mock import patch

from messor.log import setup_logging

@patch('messor.log.logging')
class TestSetupLogging(TestCase):
    def test_setup_logging_gets_root_logger(self, logging):
        setup_logging()

        logging.getLogger.assert_called_once_with('')