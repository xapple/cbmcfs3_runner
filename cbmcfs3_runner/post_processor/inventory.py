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
        Stands for "Biomass Expansion Factor, by Forest Type" we think.
        This is translated from an SQL query authored by RP.
        It calculates merchantable biomass.
        """
        pool = self.database["tblPoolIndicators"].set_index('UserDefdClassSetID')
        bef_ft = pool.join(self.classifiers, on="UserDefdClassSetID")
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
        bef_ft = bef_ft.groupby("forest_type").agg(cols_sum)
        bef_ft['Tot_Merch']  = bef_ft.SW_Merch   + bef_ft.HW_Merch
        bef_ft['Tot_ABG']    = bef_ft.SW_Merch   + bef_ft.HW_Merch + \
                               bef_ft.SW_Foliage + bef_ft.HW_Foliage + \
                               bef_ft.HW_Other   + bef_ft.SW_Other
        bef_ft['BG_Biomass'] = bef_ft.SW_Coarse  + bef_ft.SW_Fine + \
                               bef_ft.HW_Coarse  + bef_ft.HW_Fine
        bef_ft['BEF_Tot']    = (bef_ft.Tot_ABG   + bef_ft.BG_Biomass) / bef_ft.Tot_ABG
        return bef_ft

    @property_cached
    def simulated_inventory(self):
        """
        Update the inventory based on the simulation output contained in
        table 'tblPoolIndicators'.
        """
        age_indicators = self.database["tblAgeIndicators"]
        inv = (age_indicators
               .set_index('UserDefdClassSetID')
               .join(self.classifiers_coefs.set_index('UserDefdClassSetID'))
               .reset_index()
               .set_index('forest_type')
               .join(self.bef_ft, on='forest_type')
               .reset_index())
        columns_of_interest = ['AveAge', 'TimeStep', 'Area', 'Biomass', 'BEF_Tot','db']
        inv = inv[list(self.classifiers.columns) + columns_of_interest]
        inv['Merch_C_ha'] = inv.Biomass / inv.BEF_Tot
        inv['Merch_Vol_ha'] = inv.Merch_C_ha / inv.db
        return inv
