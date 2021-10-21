#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Written by Lucas Sinclair, Viorel Blujdea and Paul Rougieux.

JRC Biomass Project.
Unit D1 Bioeconomy.

See the script/compare_aidb.py for the use of this class

"""

# Built-in modules #


# First party modules #
from plumbing.cache import property_cached

# Internal modules #
from libcbm_runner.core.continent import continent as libcbm_continent


###############################################################################
class CompareAIDB(object):
    """
    This class will enable us to compare the AIDB from the old MS Access
    format supported by CBM-CFS3 with the new SQLite format supported by
    libcbm.

    You instantiate the class with a Country object from cbmcfs3_runner.
    Then you get access to the corresponding Country object from libcbm_runner.

    Then you can inspect object as so:

        >>> comp = comparisons[3]
        >>> print(comp.libcbm_aidb.db.read_df('slow_mixing_rate'))
        >>> print(comp.cbmcfs3_aidb.database['tblSlowAGtoBGTransferRate'])
    """

    def __init__(self, cbmcfs3_country):
        # Main attributes #
        self.cbmcfs3_country = cbmcfs3_country

    @property_cached
    def libcbm_country(self):
        """The matching libcbm country object."""
        return libcbm_continent.countries[self.cbmcfs3_country.iso2_code]

    @property_cached
    def cbmcfs3_aidb(self):
        return self.cbmcfs3_country.aidb

    @property_cached
    def libcbm_aidb(self):
        return self.libcbm_country.aidb

    def __call__(self):
        msg = "Comparing %s with %s."
        print(msg % (self.cbmcfs3_aidb, self.libcbm_aidb))

    def compare_table(self, table_name):
        df1 = self.libcbm_aidb.db.read_df(table_name)
        df2 = self.cbmcfs3_aidb.database[table_name]

