import unittest
from decimal import Decimal
from unittest.mock import patch, mock_open

import pydantic

from models.metals import Metals
from persistence_layer.persistence_manager import PersistenceManager


class TestPersistenceManager(unittest.TestCase):
    def setUp(self):
        self.manager = PersistenceManager(auto_init=False)

    @patch('builtins.open', new_callable=mock_open, read_data='zipcode,state,county_code,name,rate_area\n12345,NY,10,some-name,1\n67890,CA,20,some-name,2')
    def test_init_zip_code(self, mock_file):
        self.manager.init_zip_code('dummy_file_path')

        self.assertDictEqual(
            self.manager.zipcode_data,
            {
                12345: {"state": "ny", "county_code": 10, "rate_area": 1},
                67890: {"state": "ca", "county_code": 20, "rate_area": 2}
            }
        )

    def test_init_zip_code_with_raised_assertion(self):
        # Test state has 3 letters
        with patch('builtins.open', new_callable=mock_open,
                   read_data='zipcode,state,county_code,name,rate_area\n12345,NYC,10,some-name,1'):
            with self.assertRaises(pydantic.ValidationError):
                self.manager.init_zip_code('dummy_file_path')

        # Test zip code has string variables
        with patch('builtins.open', new_callable=mock_open,
                   read_data='zipcode,state,county_code,name,rate_area\n12345abc,NY,10,some-name,1'):
            with self.assertRaises(pydantic.ValidationError):
                self.manager.init_zip_code('dummy_file_path')

    @patch('builtins.open', new_callable=mock_open, read_data='plan_id,state,metal_level,rate,rate_area\n1a,NY,Silver,100.12,1\n2b,CA,Gold,200.32,2')
    def test_init_medical_plans(self, mock_file):
        self.manager.init_medical_plans('dummy_file_path')

        self.assertDictEqual(
            self.manager.plan_data,
            {
                ("ny", 1, Metals.SILVER): [{"plan_id": "1a", "rate": Decimal("100.12")}],
                ("ca", 2, Metals.GOLD): [{"plan_id": "2b", "rate": Decimal("200.32")}]
            }
        )

    def test_init_medical_plans_code_with_raised_assertion(self):
        # Test unknown metal
        with patch('builtins.open', new_callable=mock_open,
                   read_data='plan_id,state,metal_level,rate,rate_area\n1a,NY,Iron,12.34,1'):
            with self.assertRaises(pydantic.ValidationError):
                self.manager.init_medical_plans('dummy_file_path')

        # Test string rate area
        with patch('builtins.open', new_callable=mock_open,
                   read_data='plan_id,state,metal_level,rate,rate_area\n1a,NY,Silver,100.12,abc'):
            with self.assertRaises(pydantic.ValidationError):
                self.manager.init_medical_plans('dummy_file_path')

    def test_create_medical_plan_lookup_key(self):
        result = self.manager._create_medical_plan_lookup_key('ny', 1, Metals.SILVER)

        self.assertEqual(result, ('ny', 1, Metals.SILVER))

    def test_find_rates_for_zipcode(self):
        # set up the initial data
        self.manager.zipcode_data = {12345: {"state": "ny", "county_code": 10, "rate_area": 1}}
        self.manager.plan_data = {("ny", 1, Metals.SILVER): [{"plan_id": 1, "rate": Decimal("100.12")},
                                                             {"plan_id": 1, "rate": Decimal("234.31")},
                                                             {"plan_id": 1, "rate": Decimal("65.389")}]}

        result = self.manager.find_rates_for_zipcode(12345, Metals.SILVER)
        self.assertListEqual(result, [Decimal("100.12"), Decimal("234.31"), Decimal("65.389")])

    def test_find_rates_for_zipcode_not_found(self):
        # set up the initial data
        self.manager.zipcode_data = {}
        self.manager.plan_data = {}

        result = self.manager.find_rates_for_zipcode(12345, Metals.SILVER)

        self.assertIsNone(result)

    def test_find_rates_for_zipcode_lookup_not_found(self):
        # set up the initial data
        self.manager.zipcode_data = {12345: {"state": "ny", "county_code": 10, "rate_area": 1}}
        self.manager.plan_data = {}

        result = self.manager.find_rates_for_zipcode(12345, Metals.SILVER)

        self.assertIsNone(result)

    def test_find_rates_for_string_zipcode(self):
        # set up the initial data
        self.manager.zipcode_data = {12345: {"state": "ny", "county_code": 10, "rate_area": 1}}
        self.manager.plan_data = {("ny", 1, Metals.SILVER): [{"plan_id": 1, "rate": Decimal("100.12")}]}

        result = self.manager.find_rates_for_zipcode("12345", Metals.SILVER)

        self.assertListEqual(result, [Decimal("100.12")])

    def test_find_rates_for_string_zipcode(self):
        # set up the initial data
        self.manager.zipcode_data = {12345: {"state": "ny", "county_code": 10, "rate_area": 1}}
        self.manager.plan_data = {("ny", 1, Metals.SILVER): [{"plan_id": 1, "rate": Decimal("100.12")}]}

        result = self.manager.find_rates_for_zipcode("12345ab", Metals.SILVER)
        self.assertIsNone(result)

    def test_default_data_inits_correctly(self):
        manager = PersistenceManager()

