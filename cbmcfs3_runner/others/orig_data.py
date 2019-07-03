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
from cbmcfs3_runner.others.common import reshape_yields_long

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
    def inventory(self):
        """
        Columns are:

        ['status', 'forest_type', 'region', 'management_type',
         'management_strategy', 'climatic_unit', 'conifers_bradleaves',
         'UsingID', 'Age', 'Area', 'Delay', 'UNFCCCL', 'HistDist', 'LastDist']
        """
        df = self['inventory']
        # Create the age_class column
        # so it can be used as a join variable with a yields table
        df['age_class'] = (df['Age']
                           .replace('AGEID', '', regex=True)
                           .astype('int'))
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def yields(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'Sp', 'Vol0', 'Vol1', 'Vol2',
         'Vol3', 'Vol4', 'Vol5', 'Vol6', 'Vol7', 'Vol8', 'Vol9', 'Vol10',
         'Vol11', 'Vol12', 'Vol13', 'Vol14', 'Vol15', 'Vol16', 'Vol17', 'Vol18',
         'Vol19', 'Vol20', 'Vol21', 'Vol22', 'Vol23', 'Vol24', 'Vol25', 'Vol26',
         'Vol27', 'Vol28', 'Vol29', 'Vol30']
        """
        df = self['yields']
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def historical_yields(self):
        """ Historical yield taken from the xls_append object.
            The object used to append historical yield
            to the Standard Import Tool
            for the carbon pool initialisation period"""
        df = self['historical_yields']
        # Rename classifier _1, _2, _3 to forest_type, region, etc. #
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def yields_long(self):
        return reshape_yields_long(self.yields)

    @property_cached
    def historical_yields_long(self):
        return reshape_yields_long(self.historical_yields)

