#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to add an eighth classifier to every country in order to separate
the initialization period from the historical period. This is useful for
instance to switch all the yield curves of every species as soon as we hit 1995.
"""

# Built-in modules #

# Third party modules #
import pandas
from tqdm import tqdm

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.core.continent import continent

###############################################################################
class ClassifierAdder(object):
    """This class takes many of the CSV files in "export/" and changes them."""

    all_paths = """
    /export/ageclass.csv
    /export/inventory.csv
    /export/classifiers.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/transition_rules.csv
    /export/yields.csv
    /export/historical_yields.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    def __call__(self):
        for p in self.paths:
            # Read into memory #
            df = pandas.read_csv(str(p))
            # Change #
            df = df
            # Write back to disk #
            df.to_csv(str(p), index=False, float_format='%g')

###############################################################################
if __name__ == '__main__':
    adders = [ClassifierAdder(c) for c in continent]
    for adder in tqdm(adders): adder()