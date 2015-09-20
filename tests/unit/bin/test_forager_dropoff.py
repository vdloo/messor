from unittest import TestCase
from mock import patch

from bin.forager_dropoff import main

@patch('bin.forager_dropoff.drop_off')
class TestForagerDropoff(TestCase):
    def test_main_calls_drop_off(self, drop_off):
	main()

	drop_off.assert_called_once_with()
