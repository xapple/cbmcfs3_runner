#!/usr/bin/env python3
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
from autopaths.auto_paths import AutoPaths
from plumbing.cache import property_cached

# Internal modules #
from cbmcfs3_runner.pump.common import reshape_yields_long

###############################################################################
class OrigData(object):
    """
    This class will provide access to the original data of a `Country`
    as a pandas data frame. Not the input data of a Runner.
    """

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

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def __getitem__(self, item):
        return pandas.read_csv(str(self.paths[item]))

    @property_cached
    def inventory(self):
        """
        Inventory data loaded from the original calibration db through a csv file.
        Columns are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_broadleaves',
             'using_id', 'age', 'area', 'delay', 'unfcccl', 'hist_dist', 'last_dist',
             'age_class'],
        """
        # Load #
        df = self['inventory']
        # Create the age_class column so it can be
        # used as a join variable with a yields table
        df['age_class'] = (df['age']
                           .replace('AGEID', '', regex=True)
                           .astype('int'))
        # But this is only true where an age class is defined
        df['age_class'] = df['age_class'].mask(~df['using_id'])
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    @property_cached
    def yields(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'sp', 'Vol0', 'Vol1', 'Vol2',
         'Vol3', 'Vol4', 'Vol5', 'Vol6', 'Vol7', 'Vol8', 'Vol9', 'Vol10',
         'Vol11', 'Vol12', 'Vol13', 'Vol14', 'Vol15', 'Vol16', 'Vol17', 'Vol18',
         'Vol19', 'Vol20', 'Vol21', 'Vol22', 'Vol23', 'Vol24', 'Vol25', 'Vol26',
         'Vol27', 'Vol28', 'Vol29', 'Vol30']
        """
        # Load #
        df = self['yields']
        # Rename classifier _1, _2, _3 to forest_type, region, etc. #
        return df.rename(columns = self.parent.classifiers.mapping)

    @property_cached
    def historical_yields(self):
        """Historical yield taken from the original CSV file."""
        # Load #
        df = self['historical_yields']
        # Rename classifier _1, _2, _3 to forest_type, region, etc. #
        return df.rename(columns = self.parent.classifiers.mapping)

    @property_cached
    def yields_long(self):
        return reshape_yields_long(self.yields)

    @property_cached
    def historical_yields_long(self):
        return reshape_yields_long(self.historical_yields)

    @property_cached
    def disturbance_events_raw(self):
        """Load disturbance_events from the calibration database.
        Change dist_type_name to a string and Step to an integer."""
        # Load #
        df = self['disturbance_events']
        # Change dist_type_name to a string to harmonise data type.
        # some countries have a string while others have an int.
        df['dist_type_name'] = df['dist_type_name'].astype('str')
        df['step'] = df['step'].astype(int)
        # Rename classifiers #
        df = df.rename(columns = self.parent.classifiers.mapping)
        # Return #
        return df

    @property_cached
    def disturbance_events(self):
        """Load disturbance events from the calibration database.
        Add the year column."""
        # Load #
        df = self.disturbance_events_raw
        # Add year #
        df['year'] = self.parent.timestep_to_year(df['step'])
        # Return #
        return df

    @property_cached
    def disturbance_types(self):
        """Load disturbance types from the calibration database.
        Change dist_type_name to a string."""
        # Load #
        df = self['disturbance_types']
        # Cast to string #
        df['dist_type_name'] = df['dist_type_name'].astype('str')
        # Return #
        return df
