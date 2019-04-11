#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #
import pandas

# First party modules #
from autopaths.dir_path   import DirectoryPath
from autopaths.auto_paths import AutoPaths
from plumbing.logger      import create_file_logger
from plumbing.cache       import property_cached

# Internal modules #
from cbmcfs3_runner import module_dir
from cbmcfs3_runner.stdrd_import_tool.associations import Associations
from cbmcfs3_runner.others.aidb                    import AIDB

# Constants #
country_code_path = module_dir + 'extra_data/country_codes.csv'
ref_years_path    = module_dir + 'extra_data/reference_years.csv'

# Load extra data #
all_codes = pandas.read_csv(str(country_code_path))
ref_years = pandas.read_csv(str(ref_years_path))

###############################################################################
class Country(object):
    """This object gives access to the data pertaining to one country."""

    all_paths = """
    /orig/
    /orig/silviculture.sas
    /orig/aidb_eu.mdb
    /orig/calibration.mdb
    /orig/associations.csv
    /export/
    /export/ageclass.csv
    /export/classifiers.csv
    /export/coefficients.csv
    /export/disturbance_events.csv
    /export/disturbance_types.csv
    /export/inventory.csv
    /export/transition_rules.csv
    /export/yields.csv
    /logs/country.log
    """

    def __init__(self, data_dir=None):
        """Store the data directory paths where everything will start from."""
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)
        # Set country codes #
        self.set_codes()
        # Store the reference years #
        self.set_years()

    def set_codes(self):
        """Update all the country codes for this country."""
        # The reference ISO2 code #
        self.iso2_code = self.data_dir.name
        # Load name mappings #
        row = all_codes.loc[all_codes['ISO2 Code'] == self.iso2_code].iloc[0]
        # Store all the country references codes #
        self.country_num  = row['Country Code']
        self.country_name = row['Country']
        self.country_m49  = row['M49 Code']
        self.country_iso3 = row['ISO3 Code']
        # More crazy codes #
        self.nuts_zero_2006 = row['Nuts Zero 2006']
        self.nuts_zero_2016 = row['Nuts Zero 2010']

    def set_years(self):
        """Update all the reference years for this country."""
        row = ref_years.loc[ref_years['country'] == self.iso2_code].iloc[0]
        self.inventory_start_year = row['ref_year']
        self.base_year = 2015

    @property_cached
    def log(self):
        """Each runner will have its own logger."""
        return create_file_logger(self.iso2_code, self.paths.log)

    @property_cached
    def associations(self):
        return Associations(self)

    @property_cached
    def aidb(self):
        return AIDB(self)

    @property
    def map_value(self):
        """Return a float that indicates how far this country is running
        within the pipeline. This can be used to plot the country on a
        color scale map."""
        if   'run is completed' in self.paths.log.contents: return 1.0
        elif 'SIT created'      in self.paths.log.contents: return 0.5
        else:                                               return 0.0