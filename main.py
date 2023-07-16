import click
import os
import csv
import sys

from persistence_layer.persistence_manager import PersistenceManager
from models.metals import Metals


@click.command()
@click.option('--file', help='File point to the zip code rates to work out')
@click.option('--show_stderr', default=False, help='Should error logs be shown in the terminal', type=bool)
def slcsp(file, show_stderr):

    if not show_stderr:
        sys.stderr = open(os.devnull, 'w')

    persistence_manager = PersistenceManager()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(current_directory, file)

    input_zipcodes = []
    with open(path_to_file, "r") as file:
        dict_reader = csv.DictReader(file)
        for row in dict_reader:
            input_zipcodes.append(row["zipcode"])

    for zipcode in input_zipcodes:
        zipcode_rates = persistence_manager.find_rates_for_zipcode(zipcode, Metals.SILVER)
        if not zipcode_rates:
            continue

        if len(zipcode_rates) == 1:
            print("Cannot determine SLCSP because there is only a single available rate", file=sys.stderr)
            continue

        unique_sorted_rates = sorted(set(zipcode_rates))
        print(f"{zipcode}, {unique_sorted_rates[1]}")


if __name__ == '__main__':
    slcsp()
