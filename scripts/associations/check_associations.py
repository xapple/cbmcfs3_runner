#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to test if the associations.csv are good.

Typically you would run this file from a command line like this:

     ipython3.exe -i -- /deploy/cbmcfs3_runner/scripts/check_associations.py
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths
from plumbing.databases.access_database import AccessDatabase

# Internal modules #

# Constants #

###############################################################################
class AssociationsChecker(object):

    keys = ['MapAdminBoundary', 'MapEcoBoundary', 'MapSpecies',
            'MapDisturbanceType', 'MapNonForestType']

    all_paths = """
    /orig/calibration.mdb
    /orig/aidb_eu.mdb
    /orig/associations.csv
    """

    def __init__(self, country):
        # Default attributes #
        self.country = country
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.country.data_dir, self.all_paths)

    @property_cached
    def aidb(self):
        """Shortcut to the AIDB."""
        database = AccessDatabase(self.paths.aidb_eu_mdb)
        database.convert_col_names_to_snake = True
        return database

    @property_cached
    def calib(self):
        """Shortcut to the Calibration DB."""
        database = AccessDatabase(self.paths.calibration_mdb)
        database.convert_col_names_to_snake = True
        return database

    @property_cached
    def df(self):
        """Load the CSV that is 'associations.csv'."""
        self.paths.associations.must_exist()
        return pandas.read_csv(str(self.paths.associations))

    def key_to_rows(self, mapping_name):
        """
        Here is an example call:

        >>> self.key_to_rows('MapDisturbanceType')
        {'10% commercial thinning': '10% Commercial thinning',
         'Deforestation': 'Deforestation',
         'Fire': 'Wild Fire',
         'Generic 15%': 'generic 15% mortality',
         'Generic 20%': 'generic 20% mortality',
         'Generic 30%': 'generic 30% mortality',
         'Spruce Beetle 2% mortality (Ice sleet)': 'Spruce Beetle 2% mortality'}
        """
        query   = "A == '%s'" % mapping_name
        mapping = self.df.query(query).set_index('B')['C'].to_dict()
        return mapping

    def list_missing(self):
        """
        A method to predict what errors the StandardImport tool will throw
        by checking the contents of the AIDB.
        """
        # Print function #
        def print_messages(default, names, key):
            template = "%s - %s - '%s' missing from archive index database."
            for name in names:
                if name not in default:
                    print(template % (key, self.parent.parent.country_iso2, name))
        # Admin boundaries #
        default = set(self.aidb['tblAdminBoundaryDefault']['AdminBoundaryName'])
        names   = self.key_to_rows(self.keys[0]).values()
        print_messages(default, names, self.keys[0])
        # Eco boundaries #
        default = set(self.aidb['tblEcoBoundaryDefault']['EcoBoundaryName'])
        names   = self.key_to_rows(self.keys[1]).values()
        print_messages(default, names, self.keys[1])
        # Species #
        default = set(self.aidb['tblSpeciesTypeDefault']['SpeciesTypeName'])
        names   = self.key_to_rows(self.keys[2]).values()
        print_messages(default, names, self.keys[2])
        # Disturbances #
        default = set(self.aidb['tblDisturbanceTypeDefault']['dist_type_name'])
        names   = self.key_to_rows(self.keys[3]).values()
        print_messages(default, names, self.keys[3])
        # Disturbances also have to match with disturbance_types.csv #
        types = set(self.country.parent.csv_to_xls.read_csv('disturbance_types')['dist_description'])
        names = set(self.key_to_rows(self.keys[3]).keys())
        unmatched = types ^ names
        if unmatched:
            print('disturbance_types.csv - %s - %s ' % (self.parent.parent.country_iso2, unmatched))
        # Nonforest #
        default = set(self.aidb['tblAfforestationPreTypeDefault']['Name'])
        names   = self.key_to_rows(self.keys[4]).values()
        print_messages(default, names, self.keys[4])

###############################################################################
if __name__ == '__main__':
    raise Exception("This script needs to be finished and is missing a few parts.")