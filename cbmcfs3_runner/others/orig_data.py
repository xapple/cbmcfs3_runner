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

###############################################################################
class OrigData(object):
    """
    This class will provide access to the original data of a Country
    as a pandas dataframe. Not the input data of a Runner.
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
    def historical_yields(self):
        """ Historical yield table"""
        df = self['historical_yields']
        # Rename classifier _1, _2, _3 to forest_type, region, etc. #
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def yields_long(self):
        return self.reshape_yields_long(self.yields)
