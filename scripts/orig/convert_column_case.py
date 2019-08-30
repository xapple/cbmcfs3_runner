#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to convert the column names from CamelCase to snake_case.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/convet_column_case.py
"""

# Third party modules #

# Internal modules #

# Constants #

###############################################################################
# Third party modules #
from tqdm import tqdm

# First party modules #
from autopaths.auto_paths import AutoPaths

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #

###############################################################################
class CaseConverter(object):
    """
    This class takes the file "calibration.mdb" as input and generates CSVs
    from it.
    """

    all_paths = """
    /orig/coefficients.csv
    /export/
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
        pass

###############################################################################
if __name__ == '__main__':
    converters = [CaseConverter(c) for c in continent]
    for converter in tqdm(converters): converter()