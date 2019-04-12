#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to create the CSV files in the "export" directory which
are all extracted from the "calibration.mdb" database.

Typically you would run this file from a command line like this:

     ipython.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/export_orig_csv.py
"""

# Built-in modules #

# Third party modules #
from tqdm import tqdm

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #
from cbmcfs3_runner.core.continent import continent

# Constants #

###############################################################################
class ExportCalibrationCSV(object):
    """
    This class takes the file "calibration.mdb" as input and generates CSVs
    from it.
    """

    all_paths = """
    /orig/
    /export/ageclass.csv
    /export/classifiers.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/inventory.csv
    /export/transition_rules.csv
    /export/yields.csv
    /export/coefficients.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    file_to_table_name = {
        "ageclass":                     "Age Classes_CBM",
        "inventory":                    "Back_Inventory",
        "classifiers":                  "Classifiers",
        "coefficients":                 "Coefficients",
        "disturbance_types":            "Disturbance Types_CBM",
        "disturbance_events":           "Dist_Events_Const",
        "yields":                       "SELECTED_CURRENT_YTS",
        "transition_rules":             "TRANSITION_CBM",
    }

    @property_cached
    def database(self): return AccessDatabase(self.country.paths.calibration_mdb)

    def check(self):
        """Check that each table exists."""
        for filename, table_name in self.file_to_table_name.items():
            if table_name not in self.database:
                print("Table '%s' is missing from '%s'." % (table_name, self.database))

    def __call__(self):
        """Extract several queries from the database into CSV files."""
        # Make each file #
        for file_name, table_name in self.file_to_table_name.items():
            destination = str(self.paths[file_name])
            self.database[table_name].to_csv(destination, index=False)

    def move_coefs(self):
        """The coefficients file is a bit special. We will change one line.
        And move it to orig as it is constant per country."""
        # Get the path #
        coef_file = self.paths.coefficients
        # Rename column 'Species' #

        # Move it #
        coef_file.move_to(self.paths.orig_dir)

###############################################################################
if __name__ == '__main__':
    exporters = [ExportCalibrationCSV(c) for c in continent]
    for exporter in tqdm(exporters):
        exporter.check()
        exporter()
        exporter.move_coefs()


