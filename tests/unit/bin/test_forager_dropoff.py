from unittest import TestCase
from mock import patch

from bin.forager_dropoff import main

class TestForagerDropoff(TestCase):
    def setUp(self):
        patcher = patch('bin.forager_dropoff.drop_off')
        self.addCleanup(patcher.stop)
        self.drop_off = patcher.start()

    def test_main_calls_drop_off(self):
	main()

	self.drop_off.assert_called_once_with()
