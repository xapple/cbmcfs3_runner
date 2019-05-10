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
class InputData(object):
    """
    This class will provide access to the input data of a Runner
    as a pandas dataframe.
    """

    all_paths = """
    /input/xls/input_tables.xls
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.data_dir, self.all_paths)

    def copy_from_country(self):
        destination_dir = self.parent.paths.csv_dir
        destination_dir.remove()
        self.parent.country.paths.export_dir.copy(destination_dir)

    @property_cached
    def xls(self):
        """The excel file"""
        return pandas.ExcelFile(str(self.paths.xls))

    #-------------------------- Specific sheets ------------------------------#
    @property_cached
    def inventory(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'UsingID', 'Age', 'Area',
        'Delay', 'UNFCCCL', 'HistDist', 'LastDist']
        """
        return self.xls.parse("Inventory")

    @property_cached
    def disturbance_events(self):
        """
        Columns are:

        ['_1', '_2', '_3', '_4', '_5', '_6', '_7', 'UsingID', 'SWStart', 'SWEnd',
        'HWStart', 'HWEnd', 'Min_since_last_Dist', 'Max_since_last_Dist',
        'Last_Dist_ID', 'Min_tot_biom_C', 'Max_tot_biom_C',
        'Min_merch_soft_biom_C', 'Max_merch_soft_biom_C',
        'Min_merch_hard_biom_C', 'Max_merch_hard_biom_C', 'Min_tot_stem_snag_C',
        'Max_tot_stem_snag_C', 'Min_tot_soft_stem_snag_C',
        'Max_tot_soft_stem_snag_C', 'Min_tot_hard_stem_snag_C',
        'Max_tot_hard_stem_snag_C', 'Min_tot_merch_stem_snag_C',
        'Max_tot_merch_stem_snag_C', 'Min_tot_merch_soft_stem_snag_C',
        'Max_tot_merch_soft_stem_snag_C', 'Min_tot_merch_hard_stem_snag_C',
        'Max_tot_merch_hard_stem_snag_C', 'Efficency', 'Sort_Type',
        'Measurement_type', 'Amount', 'Dist_Type_ID', 'Step']
        """
        return self.xls.parse("DistEvents")

    @property_cached
    def disturbance_types(self):
        return self.xls.parse("DistType")

    @property_cached
    def ageclass(self):
        return self.xls.parse("AgeClasses")

    @property_cached
    def classifiers(self):
        df = self.xls.parse("Classifiers")
        sort_by = ['ClassifierNumber', 'ClassifierValueID']
        return df.sort_values(by=sort_by, ascending=[True, False])