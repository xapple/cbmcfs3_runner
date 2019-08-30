#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to convert the column names from CamelCase to snake_case.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/convert_column_case.py
"""

# Third party modules #
import pandas
from tqdm import tqdm

# First party modules #
from autopaths.auto_paths import AutoPaths
from plumbing.common import camel_to_snake

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #

###############################################################################
class CaseConverter(object):
    """
    This class takes many of the CSV files in export/ and orig/ and
    converts their title case.
    """

    all_paths = """
    /orig/coefficients.csv
    /orig/silv_treatments.csv
    /export/ageclass.csv
    /export/inventory.csv
    /export/classifiers.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/transition_rules.csv
    /export/yields.csv
    /export/historical_yields.csv
    /fusion/back_inventory_aws.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        for p in self.paths:
            # Skip some fusion files #
            if not p: continue
            # Read #
            df = pandas.read_csv(str(p))
            # Change #
            df = df.rename(columns = camel_to_snake)
            # Write #
            df.to_csv(str(p), index=False)

###############################################################################
if __name__ == '__main__':
    converters = [CaseConverter(c) for c in continent]
    for converter in tqdm(converters): converter()