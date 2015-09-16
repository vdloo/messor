from unittest import TestCase
from mock import patch

from bin.forager_pickup import main

@patch('bin.forager_pickup.pick_up')
class TestForagerPickup(TestCase):
    def test_main_calls_pick_up(self, pick_up):
	main()

	pick_up.assert_called_once_with()
