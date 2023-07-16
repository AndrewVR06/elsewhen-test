import csv
import os
import sys
from functools import lru_cache
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Union, Optional
from models.metals import Metals
from models.zip import Zip
from models.plan import Plan
from pydantic import ValidationError


class PersistenceManager:
    zipcode_data: Dict[int, Dict[str, Any]]  # Hold the zip data in memory
    plan_data: Dict[Tuple[str, int, Metals], List[Dict[str, Any]]]  # Hold the plan data in memory

    def __init__(self, auto_init=True, zipcode_file="zips.csv", medical_plans_file="plans.csv"):
        # Initialise our base data - this would typically be found in our database
        if auto_init:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            self.init_zip_code(os.path.join(current_directory, zipcode_file))
            self.init_medical_plans(os.path.join(current_directory, medical_plans_file))

    @lru_cache(maxsize=1024)
    def _create_medical_plan_lookup_key(self, state: str, rate_area: int, metal: Metals) -> Tuple[str, int, Metals]:
        """
        Helper function to create a standardised lookup key for accessing plan data
        """
        return state, rate_area, metal

    def init_zip_code(self, file_path: str):
        """
        Initialise the zips.csv as our base data
        In a typical system, this data would be in our database
        """
        self.zipcode_data = {}

        with open(file_path, "r") as file:
            dict_reader = csv.DictReader(file)

            for row in dict_reader:
                try:
                    data = Zip(**row)
                    self.zipcode_data[data.zipcode] = {"state": data.state, "county_code": data.county_code, "rate_area": data.rate_area}
                except ValidationError as e:
                    # We would typically get track of validation that may occur here to display back to the user
                    print(f"Row {row} had failed validation")
                    raise e

    def init_medical_plans(self, file_path: str):
        """
        Initialise all medical plan data
        """
        self.plan_data = {}

        with open(file_path, "r") as file:
            dict_reader = csv.DictReader(file)

            for row in dict_reader:
                try:
                    data = Plan(**row)
                    key = self._create_medical_plan_lookup_key(data.state, data.rate_area, data.metal_level)

                    # If plan data already exists with the given key, then simply add more information to it
                    if self.plan_data.get(key):
                        self.plan_data[key].append({"plan_id": data.plan_id, "rate": data.rate})
                    else:
                        self.plan_data[key] = [{"plan_id": data.plan_id, "rate": data.rate}]

                except ValidationError as e:
                    # We would typically get track of validation that may occur here to display back to the user
                    print(f"Row {row} had failed validation")
                    raise e

    def find_rates_for_zipcode(self, zipcode: Union[str, int], metal_plan: Metals) -> Optional[List[Decimal]]:
        """
        Given a zipcode and metal plan, find all rates applicable
        :param zipcode:
        :param metal_plan:
        :return:
        """
        if type(zipcode) is str:
            try:
                zipcode = int(zipcode)
            except ValueError:
                print(f"Zipcode {zipcode} is not a valid integer")
                return None

        zipcode_data = self.zipcode_data.get(zipcode)
        if zipcode_data is None:
            print(f"Zipcode {zipcode} does not exist in our dataset", file=sys.stderr)
            return None

        lookup_key = self._create_medical_plan_lookup_key(zipcode_data["state"], zipcode_data["rate_area"], metal_plan)

        if (plan_data := self.plan_data.get(lookup_key)) is None:
            print(f"Medical plan data does not exist for the given lookup key {lookup_key}", file=sys.stderr)
            return None

        # Using a lookup key, retrieve all plan data. Then return all rate information for that plan
        return list(map(lambda area_information: area_information["rate"], plan_data))
