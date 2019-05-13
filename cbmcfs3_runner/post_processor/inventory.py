#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair and Paul Rougieux.

JRC biomass Project.
Unit D1 Bioeconomy.
"""

# Built-in modules #

# Third party modules #

# First party modules #
from plumbing.cache import property_cached
from autopaths.auto_paths import AutoPaths

# Internal modules #

###############################################################################
class Inventory(object):
    """
    See notebook "simulated_inventory.ipynb" for more details.
    """

    all_paths = """
    /output/inventory/
    """

    def __init__(self, parent):
        # Default attributes #
        self.parent = parent
        # Directories #
        self.paths = AutoPaths(self.parent.parent.data_dir, self.all_paths)

    @property_cached
    def bef_ft(self):
        """
        Stands for "Biomass Expansion Factor, by Forest Type", we think.
        This is translated from an SQL query authored by RP.
        It calculates merchantable biomass.
        """
        # Load tables #
        pool  = self.parent.database["tblPoolIndicators"].set_index('UserDefdClassSetID')
        clifr = self.parent.classifiers
        # Join #
        df = pool.join(clifr, on="UserDefdClassSetID")
        # Sum for everyone #
        cols_sum = {'SW_Merch'  : 'sum',
                    'SW_Foliage': 'sum',
                    'SW_Other'  : 'sum',
                    'HW_Merch'  : 'sum',
                    'HW_Foliage': 'sum',
                    'HW_Other'  : 'sum',
                    'SW_Coarse' : 'sum',
                    'SW_Fine'   : 'sum',
                    'HW_Coarse' : 'sum',
                    'HW_Fine'   : 'sum'}
        # Group and aggregate #
        df = df.groupby("forest_type").agg(cols_sum).reset_index()
        # Make new columns #
        df['Tot_Merch']  = df.SW_Merch   + df.HW_Merch
        df['Tot_ABG']    = df.SW_Merch   + df.HW_Merch   + \
                           df.SW_Foliage + df.HW_Foliage + \
                           df.HW_Other   + df.SW_Other
        df['BG_Biomass'] = df.SW_Coarse  + df.SW_Fine    + \
                           df.HW_Coarse  + df.HW_Fine
        df['BEF_Tot']    = (df.Tot_ABG   + df.BG_Biomass) / df.Tot_ABG
        # Return result #
        return df

    @property_cached
    def simulated(self):
        """
        Update the inventory based on the simulation output contained in
        table 'tblPoolIndicators'.

        Columns of the output are:

            ['status', 'forest_type', 'region', 'management_type',
             'management_strategy', 'climatic_unit', 'conifers_bradleaves', 'AveAge',
             'TimeStep', 'Area', 'Biomass', 'BEF_Tot', 'db', 'Merch_C_ha',
             'Merch_Vol_ha']
        """
        # Load table #
        age_indicators = self.parent.database["tblAgeIndicators"]
        classifr_coefs = self.parent.classifiers_coefs
        # Set the same index #
        age_indicators = age_indicators.set_index('UserDefdClassSetID')
        classifr_coefs = classifr_coefs.set_index('UserDefdClassSetID')
        # Double join #
        df = (age_indicators
               .join(classifr_coefs)
               .reset_index()
               .set_index('forest_type')
               .join(self.bef_ft.set_index('forest_type'))
               .reset_index())
        # Select only some columns #
        columns_of_interest  = ['AveAge', 'TimeStep', 'Area', 'Biomass', 'BEF_Tot','db']
        columns_of_interest += list(self.parent.classifiers.columns)
        df = df[columns_of_interest].copy()
        # Divide #
        df['Merch_C_ha']   = df.Biomass    / df.BEF_Tot
        df['Merch_Vol_ha'] = df.Merch_C_ha / df.db
        # Return result #
        return df
