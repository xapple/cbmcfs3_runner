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
from plumbing.common import camel_to_snake

# Internal modules #

###############################################################################
class InputData(object):
    """
    This class will provide access to the input data of a Runner
    as a pandas data frame.
    """

    all_paths = """
    /input/xls/default_tables.xls
    /input/xls/append_tables.xls
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)
        # Shortcut for classifiers names #
        self.classifiers_mapping = self.parent.country.classifiers.mapping

    #--------------------- Access the spreadsheets ---------------------------#
    @property_cached
    def xls(self):
        """The first excel file."""
        return pandas.ExcelFile(str(self.paths.default))

    @property_cached
    def xls_append(self):
        """The second excel file."""
        return pandas.ExcelFile(str(self.paths.append))

    #-------------------------- Other methods --------------------------------#
    def get_sheet(self, name):
        """Get a specific sheet in the first excel."""
        df = self.xls.parse(name)
        df = df.rename(columns=camel_to_snake)
        return df

    #-------------------------- Specific sheets ------------------------------#
    @property_cached
    def disturbance_events(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'using_id', 'sw_start', 'sw_end',
         'hw_start', 'hw_end', 'min_since_last_dist', 'max_since_last_dist',
         'last_dist_id', 'min_tot_biom_c', 'max_tot_biom_c',
         'min_merch_soft_biom_c', 'max_merch_soft_biom_c',
         'min_merch_hard_biom_c', 'max_merch_hard_biom_c', 'min_tot_stem_snag_c',
         'max_tot_stem_snag_c', 'min_tot_soft_stem_snag_c',
         'max_tot_soft_stem_snag_c', 'min_tot_hard_stem_snag_c',
         'max_tot_hard_stem_snag_c', 'min_tot_merch_stem_snag_c',
         'max_tot_merch_stem_snag_c', 'min_tot_merch_soft_stem_snag_c',
         'max_tot_merch_soft_stem_snag_c', 'min_tot_merch_hard_stem_snag_c',
         'max_tot_merch_hard_stem_snag_c', 'efficiency', 'sort_type',
         'measurement_type', 'amount', 'dist_type_name', 'step']
        """
        # Get the right sheet #
        df = self.get_sheet("DistEvents")
        # Harmonize the dist_type_id data type amongst countries
        df['dist_type_name'] = df['dist_type_name'].astype(str)
        # Return #
        return df

    @property_cached
    def disturbance_types(self):
        """
        Columns are: ['dist_type_name', 'name']
        """
        # Get the right sheet #
        df = self.get_sheet("DistType")
        # dist_type_name has to be strings for joining purposes #
        df['dist_type_name'] = df['dist_type_name'].astype(str)
        # Return #
        return df