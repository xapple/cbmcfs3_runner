#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to create the CSV files in the "export" directory which
are all extracted from the "calibration.mdb" database.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/orig/export_orig_csv.py
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

    file_to_table_name = {
        "coefficients":                 "Coefficients",
        "ageclass":                     "Age Classes_CBM",
        "inventory":                    "Back_Inventory",
        "classifiers":                  "Classifiers",
        "disturbance_types":            "Disturbance Types_CBM",
        "disturbance_events":           "Dist_Events_Const",
        "transition_rules":             "TRANSITION_CBM",
        "yields":                       "SELECTED_CURRENT_YTS",
        "historical_yields":            "SELECTED_HISTORICAL_YTS",
    }

    @property_cached
    def database(self):
        database = AccessDatabase(self.country.paths.calibration_mdb)
        database.convert_col_names_to_snake = True
        return database

    def check(self):
        """Check that each table exists."""
        for filename, table_name in self.file_to_table_name.items():
            if table_name not in self.database:
                print("Table '%s' is missing from '%s'." % (table_name, self.database))

    def remove_directory(self):
        self.paths.export_dir.remove()

    def run_queries(self):
        """Extract several queries from the database into CSV files."""
        # Make each file #
        for file_name, table_name in self.file_to_table_name.items():
            destination = str(self.paths[file_name])
            # Load from database #
            df = self.database[table_name]
            # Special renaming - TODO check this works #
            df = df.rename(columns = {'conifers_bradleaves': 'broad_conifers'})
            df = df.rename(columns = {'forest_type':         'species'})
            # Export #
            df.to_csv(destination, index=False)

    def rename_coefs(self):
        """The coefficients file is a bit special. We will change one line.
        And move it to /orig/ as it is constant per country."""
        # Get the path #
        coef_file = self.paths.coefficients
        # Rename column 'Species' to match classifier 2's name #
        coef_file.replace_line('ID,Species,C,DB,Harvest_Gr',
                               'ID,Forest type,C,DB,Harvest_Gr')

###############################################################################
if __name__ == '__main__':
    exporters = [ExportCalibrationCSV(c) for c in continent]
    for exporter in tqdm(exporters):
        exporter.check()
        exporter.remove_directory()
        exporter.run_queries()
        exporter.rename_coefs()


