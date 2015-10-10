from unittest import TestCase
from mock import patch

from messor.log import setup_logging

class TestSetupLogging(TestCase):
    def setUp(self):
        patcher = patch('messor.log.logging')
        self.addCleanup(patcher.stop)
        self.logging = patcher.start()

    def test_setup_logging_gets_root_logger(self):
        setup_logging()

        self.logging.getLogger.assert_called_once_with('')
