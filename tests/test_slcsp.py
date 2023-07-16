import unittest
from unittest.mock import patch, mock_open, call
from persistence_layer.persistence_manager import PersistenceManager
from main import slcsp
from click.testing import CliRunner
from decimal import Decimal


class TestPersistenceManager(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open, read_data='zipcode,rate\n12345,')
    @patch('persistence_layer.persistence_manager.PersistenceManager', autospec=True)
    @patch('persistence_layer.persistence_manager.PersistenceManager.__init__', return_value=None)
    @patch.object(PersistenceManager, 'find_rates_for_zipcode',
                  return_value=[Decimal("100.12"), Decimal("234.31"), Decimal("65.389")])
    def test_slcsp_success(self, mock_find_rates, mock_man_init, mock_manager, mock_file, mock_print):
        self.runner.invoke(slcsp, ["--file", "dummy_file_path"])
        assert mock_print.call_args == call('12345, 100.12')

    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open, read_data='zipcode,rate\n12345,')
    @patch('persistence_layer.persistence_manager.PersistenceManager', autospec=True)
    @patch('persistence_layer.persistence_manager.PersistenceManager.__init__', return_value=None)
    @patch.object(PersistenceManager, 'find_rates_for_zipcode',
                  return_value=[Decimal("100.12")])
    def test_slcsp_single_rate(self, mock_find_rates, mock_man_init, mock_manager, mock_file, mock_print):
        self.runner.invoke(slcsp, ["--file", "dummy_file_path"])

        latest_print_call = mock_print.call_args[0]
        assert latest_print_call == ("Cannot determine SLCSP because there is only a single available rate", )

    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open, read_data='zipcode,rate\n12345,')
    @patch('persistence_layer.persistence_manager.PersistenceManager', autospec=True)
    @patch('persistence_layer.persistence_manager.PersistenceManager.__init__', return_value=None)
    @patch.object(PersistenceManager, 'find_rates_for_zipcode',
                  return_value=[])
    def test_slcsp_no_rates(self, mock_find_rates, mock_man_init, mock_manager, mock_file, mock_print):
        self.runner.invoke(slcsp, ["--file", "dummy_file_path"])
        self.assertIsNone(mock_print.call_args)

