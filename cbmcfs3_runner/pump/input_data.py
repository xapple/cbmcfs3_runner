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
from cbmcfs3_runner.pump.common import reshape_yields_long

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
        # Classifiers names #
        self.classifiers_mapping = self.parent.country.classifiers.mapping

    def copy_from_country(self):
        destination_dir = self.parent.paths.csv_dir
        destination_dir.remove()
        self.parent.country.paths.export_dir.copy(destination_dir)

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
        """Get a specific sheet in the first excel"""
        df = self.xls.parse(name)
        df = df.rename(columns=camel_to_snake)
        return df

    #-------------------------- Specific sheets ------------------------------#
    @property_cached
    def inventory(self):
        """
        Columns are:

        ['status', 'forest_type', 'region', 'management_type',
         'management_strategy', 'climatic_unit', 'conifers_broadleaves',
         'using_id', 'age', 'area', 'delay', 'unfcccl', 'hist_dist', 'last_dist']
        """
        # Get the right sheet #
        df = self.get_sheet("Inventory")
        # Create the age_class column
        # so it can be used as a join variable with a yields table
        df['age_class'] = (df['age']
                           .replace('AGEID', '', regex=True)
                           .astype('int'))
        return df.rename(columns = self.classifiers_mapping)

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
         'measurement_type', 'amount', 'dist_type_id', 'step']
        """
        # Get the right sheet #
        df = self.get_sheet("DistEvents")
        # Harmonise Dist_Type_ID data type amoung countries
        # some have int, others have str, make it str for all.
        df['dist_type_id'] = df['dist_type_id'].astype(str)
        return df

    @property_cached
    def disturbance_types(self):
        """
        Columns are: ['disturbance_type_id', 'name']
        """
        # Get the right sheet #
        df = self.get_sheet("DistType")
        # disturbance_type_id has to be strings for joining purposes #
        df['disturbance_type_id'] = df['disturbance_type_id'].astype(str)
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
        # Get the right sheet #
        df = self.get_sheet("Growth")
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def historical_yields(self):
        """
        Historical yield taken from the xls_append object.
        The object used to append historical yield
        to the Standard Import Tool
        for the carbon pool initialization period
        """
        # Get the right sheet #
        df = self.get_sheet("Growth")
        # Rename classifier _1, _2, _3 to forest_type, region, etc. #
        return df.rename(columns = self.classifiers_mapping)

    @property_cached
    def yields_long(self):
        return reshape_yields_long(self.yields)

    @property_cached
    def historical_yields_long(self):
        return reshape_yields_long(self.historical_yields)

    @property_cached
    def ageclass(self):
        # Get the right sheet #
        return self.get_sheet("AgeClasses")

    @property_cached
    def classifiers(self):
        # Get the right sheet #
        df = self.get_sheet("Classifiers")
        sort_by = ['classifier_number', 'classifier_value_id']
        return df.sort_values(by=sort_by, ascending=[True, False])


