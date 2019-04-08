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

# Internal modules #
from cbmcfs3_runner import repos_dir
from cbmcfs3_runner.runner import Runner

# Country codes #
all_codes = pandas.read_csv(str(repos_dir + 'data/faostat_countries.csv'))

# Reference years #
ref_years = pandas.read_csv(str(repos_dir + 'data/reference_years.csv'))

###############################################################################
class Country(Runner):
    """This object is represents the data and simulation pertaining to one
    euro country. This object will have several Runner instances to prepare
    and run the different simulations needed."""

    def __init__(self, data_dir=None):
        """Store the data directory paths where everything will start from."""
        # Main directory #
        self.data_dir = DirectoryPath(data_dir)
        # Check it exists #
        self.data_dir.must_exist()
        # Automatically access paths based on a string of many subpaths #
        self.paths = AutoPaths(self.data_dir, self.all_paths)
        # The reference ISO2 code #
        self.country_iso2 = self.data_dir.name
        # Store all the country references codes #
        row = all_codes.loc[all_codes['ISO2 Code'] == self.country_iso2].iloc[0]
        self.country_num  = row['Country Code']
        self.country_name = row['Country']
        self.country_m49  = row['M49 Code']
        self.country_iso3 = row['ISO3 Code']
        # More crazy codes #
        self.nuts_zero_2006 = row['Nuts Zero 2006']
        self.nuts_zero_2016 = row['Nuts Zero 2010']
        # Store the reference years #
        row = ref_years.loc[ref_years['country'] == self.country_iso2].iloc[0]
        self.inventory_start_year = row['ref_year']
        self.base_year = 2015

    @property
    def map_value(self):
        """Return a float that indicates how far this country is running.
        This can be used to plot the country on a map."""
        if   'run is completed' in self.paths.log.contents: return 1.0
        elif 'SIT created'      in self.paths.log.contents: return 0.5
        else:                                               return 0.0