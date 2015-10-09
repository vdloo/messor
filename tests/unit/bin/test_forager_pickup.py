from unittest import TestCase
from mock import patch

from bin.forager_pickup import main

class TestForagerPickup(TestCase):
    def setUp(self):
	patcher = patch('bin.forager_pickup.pick_up')
	self.addCleanup(patcher.stop)
	self.pick_up = patcher.start()

    def test_main_calls_pick_up(self):
	main()

	self.pick_up.assert_called_once_with()
